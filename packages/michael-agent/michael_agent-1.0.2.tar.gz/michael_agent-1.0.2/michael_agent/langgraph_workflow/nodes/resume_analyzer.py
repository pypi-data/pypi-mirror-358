"""
Resume Analyzer Node
Combines resume parsing and scoring functionality to:
1. Extract text from resume PDFs
2. Parse resumes to extract candidate details (name, email, phone, skills, experience, education)
3. Score the resume relevance against the job description
"""

import os
import logging
import json
import time
import re
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random
# Import OpenAI for embeddings and analysis
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.messages import HumanMessage

# PDF parsing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#######################################################
# Document Parsing Section
#######################################################

class DocumentParser:
    """Base class for document parsers"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a document file"""
        raise NotImplementedError("Subclasses must implement this method")

class PyPDF2Parser(DocumentParser):
    """Parser using PyPDF2"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a PDF using PyPDF2"""
        if not file_path.lower().endswith('.pdf'):
            logger.warning(f"PyPDF2 can only parse PDF files, received: {file_path}")
            return ""
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                try:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                except PyPDF2.errors.PdfReadError as e:
                    logger.error(f"PyPDF2 error reading file {file_path}: {str(e)}")
                    return ""
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF with PyPDF2: {str(e)}")
            return ""

class PyMuPDFParser(DocumentParser):
    """Parser using PyMuPDF"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a PDF using PyMuPDF"""
        if not file_path.lower().endswith('.pdf'):
            logger.warning(f"PyMuPDF can only parse PDF files, received: {file_path}")
            return ""
        
        try:
            text = ""
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()  # Important to close the document to avoid resource leaks
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF with PyMuPDF: {str(e)}")
            return ""

class TextFileParser(DocumentParser):
    """Parser for text files"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            return ""

def get_parser(file_path: str) -> DocumentParser:
    """Get the appropriate parser for the given file path"""
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Invalid file path: {file_path}")
        return TextFileParser()  # Default to text parser which will handle the error
        
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Use parsers based on file extension
    if file_extension == '.pdf':
        # Try PyMuPDF first, then fall back to PyPDF2 if not available
        if PYMUPDF_AVAILABLE:
            logger.info(f"Using PyMuPDF parser for {file_path}")
            return PyMuPDFParser()
        elif PYPDF2_AVAILABLE:
            logger.info(f"Using PyPDF2 parser for {file_path}")
            return PyPDF2Parser()
    
    # Default to text file parser
    return TextFileParser()

def extract_basic_info(text: str) -> Dict[str, Any]:
    """Extract basic information from resume text"""
    data = {
        "name": None,
        "email": None,
        "phone": None,
        "skills": [],
        "education": [],
        "experience": [],
        "raw_content": text
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        data["email"] = email_matches[0]
    
    # Extract phone
    phone_pattern = r'\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        data["phone"] = phone_matches[0]
    
    # Attempt to extract name (very basic)
    lines = text.split('\n')
    if lines and lines[0].strip():
        potential_name = lines[0].strip()
        if len(potential_name.split()) <= 3 and len(potential_name) < 40:
            data["name"] = potential_name
    
    # Try to extract additional information using LLM
    try:
        data.update(extract_resume_data_with_llm(text))
    except Exception as e:
        logger.warning(f"Error extracting data with LLM: {str(e)}")
    
    return data

def extract_resume_data_with_llm(text: str) -> Dict[str, Any]:
    """Use Azure OpenAI to extract more detailed information from the resume"""
    if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
        return {}
    
    try:
        llm = AzureChatOpenAI(
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY
        )
        
        system_prompt = """
        Extract the following information from the resume text:
        1. A list of skills (technical and soft skills)
        2. Education history (degree, institution, year)
        3. Work experience (company, position, duration, responsibilities)
        
        Format the output as a JSON object with the following structure:
        {
            "skills": ["skill1", "skill2", ...],
            "education": [{"degree": "...", "institution": "...", "year": "..."}],
            "experience": [{"company": "...", "position": "...", "duration": "...", "responsibilities": "..."}]
        }
        """
        
        # Truncate text if it's too long
        max_tokens = 6000
        text = text[:max_tokens] if len(text) > max_tokens else text
        
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ])
        
        # Extract JSON from response
        content = response.content
        # Find JSON part in the response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
        
        return {}
    except Exception as e:
        logger.error(f"Error extracting data with LLM: {str(e)}")
        return {}

#######################################################
# Resume Scoring Section
#######################################################

def create_azure_openai_client():
    """Create and configure the Azure OpenAI client for chat completions"""
    try:
        # Use the correct parameter names for Azure OpenAI
        api_key = settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY or settings.OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT or settings.OPENAI_API_BASE
        api_version = settings.AZURE_OPENAI_API_VERSION or settings.OPENAI_API_VERSION
        deployment = settings.AZURE_OPENAI_DEPLOYMENT
        
        client = AzureChatOpenAI(
            temperature=0.3,
            azure_deployment=deployment,
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        
        logger.info(f"Created Azure OpenAI Chat client with deployment {deployment}")
        return client
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
        return None

def create_embeddings_client():
    """Create embeddings client for similarity calculations"""
    # This function is kept for backward compatibility but is not used in the LLM-only approach
    logger.info("Embeddings client creation skipped - using direct LLM approach instead")
    return None

def extract_resume_sections(resume_text: str) -> Dict[str, str]:
    """Extract key sections from resume text"""
    sections = {
        "skills": "",
        "experience": "",
        "education": "",
        "full": resume_text
    }
    
    # Very basic section extraction based on common headers
    lines = resume_text.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check for common section headers
        if "skills" in line_lower or "technical skills" in line_lower or "competencies" in line_lower:
            current_section = "skills"
            continue
        elif "experience" in line_lower or "employment" in line_lower or "work history" in line_lower:
            current_section = "experience"
            continue
        elif "education" in line_lower or "academic" in line_lower or "qualifications" in line_lower:
            current_section = "education"
            continue
        
        # Add content to current section
        if current_section and current_section in sections:
            sections[current_section] += line + "\n"
    
    return sections

def extract_jd_sections(jd_text: str) -> Dict[str, str]:
    """Extract key sections from job description text"""
    sections = {
        "responsibilities": "",
        "requirements": "",
        "full": jd_text
    }
    
    # Very basic section extraction based on common headers
    lines = jd_text.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check for common section headers
        if "responsibilities" in line_lower or "duties" in line_lower or "what you'll do" in line_lower:
            current_section = "responsibilities"
            continue
        elif "requirements" in line_lower or "qualifications" in line_lower or "skills" in line_lower:
            current_section = "requirements"
            continue
        
        # Add content to current section
        if current_section and current_section in sections:
            sections[current_section] += line + "\n"
    
    return sections

def compute_similarity_score_llm(client, resume_text: str, jd_text: str) -> float:
    """Compute similarity score between resume and job description using LLM"""
    try:
        # Truncate texts if they are too long for the LLM context window
        resume_truncated = resume_text[:2000]  # Adjust based on your LLM's limits
        jd_truncated = jd_text[:2000]  # Adjust based on your LLM's limits
        
        # Create the prompt
        prompt = f"""
        Your task is to compare a resume and job description to determine how well the candidate matches the job requirements.
        
        Job Description:
        {jd_truncated}
        
        Resume:
        {resume_truncated}
        
        Based on the match between the resume and job description, provide a relevance score between 0.0 and 1.0, 
        where 1.0 means perfect match and 0.0 means no match at all.
        
        Return only a single float value between 0.0 and 1.0 without any explanation.
        """
        
        # Get the response from LLM
        response = client.invoke([HumanMessage(content=prompt)])
        
        # Parse the response to extract the score
        score_text = response.content.strip()
        
        # Attempt to parse the score from text
        try:
            # Handle if model returns additional text with the score
            score = float(''.join(c for c in score_text if c.isdigit() or c == '.'))
            # Ensure score is within bounds
            score = min(max(score, 0.0), 1.0)
            return score
        except ValueError:
            # If we can't parse a score, use a default value
            logger.error(f"Failed to parse score from LLM response: {score_text}")
            return 0.5
    except Exception as e:
        logger.error(f"Error computing similarity score with LLM: {str(e)}")
        return 0.0

#######################################################
# Combined Resume Analyzer Node
#######################################################

def analyze_resume(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a resume against job requirements"""
    logger.info("Starting resume analysis...")
    try:
        # Skip if no resume path is provided
        resume_path = state.get("resume_path")
        if not resume_path:
            error_message = "No resume path provided for analysis"
            logger.error(error_message)
            
            # Add error to state
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "step": "resume_analyzer",
                "error": error_message
            })
            return state
        
        # Check if resume was already processed
        resume_text = state.get("resume_text")
        if not resume_text:
            # Load resume
            resume_text = load_resume(resume_path)
            if not resume_text:
                error_message = f"Failed to load resume text from {resume_path}"
                logger.error(error_message)
                
                # Add error to state
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "resume_analyzer",
                    "error": error_message
                })
                return state
            
            # Update state with resume text
            state["resume_text"] = resume_text
        
        # Extract basic details from resume
        if not state.get("resume_data"):
            state["resume_data"] = extract_resume_details(resume_text)
            
            # Update candidate info in state
            if state["resume_data"]:
                state["candidate_name"] = state["resume_data"].get("name")
                state["candidate_email"] = state["resume_data"].get("email")
                logger.info(f"Extracted candidate info: {state['candidate_name']} - {state['candidate_email']}")
        
        # Load job description using the timestamp-based job ID
        job_id = state.get("job_id")
        if not job_id:
            error_message = "Missing job ID for resume analysis"
            logger.error(error_message)
            print("[RESUME_ANALYZER] ERROR: No job ID found in state")
            
            # Add error to state
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "step": "resume_analyzer",
                "error": error_message
            })
            return state
        
        # Instead of getting JD text from state, read it from file
        from utils.jd_utils import load_job_description

        job_file_path = os.path.join("job_descriptions", f"{job_id}.json")
        
        # Print debug information
        print(f"[RESUME_ANALYZER] Looking for job description file: {job_file_path}")
        
        # Use the utility function to load job description
        job_data = load_job_description(job_id=job_id, job_file_path=job_file_path)
        if job_data:
            jd_text = job_data.get("job_description", "")
            # Add debug print statement to verify JD content
            print(f"[RESUME_ANALYZER] JOB DESCRIPTION LOADED for job_id {job_id}. First 200 chars: {jd_text[:200]}...")
            logger.info(f"[RESUME_ANALYZER] Successfully loaded job description for job_id {job_id} with length {len(jd_text)}")
            
            # Update the state with the job description text
            state["job_description_text"] = jd_text
            state["job_description"] = job_data
        else:
            error_message = f"Missing job description for scoring (job_id: {job_id})"
            logger.error(error_message)
            print(f"[RESUME_ANALYZER] ERROR: Could not load job description for job_id {job_id}")
            
            # Add error to state
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "step": "resume_analyzer",
                "error": error_message
            })
            return state
            
        # Create LLM client for direct scoring
        chat_client = create_azure_openai_client()
        if not chat_client:
            logger.warning("Failed to initialize Azure OpenAI client, falling back to random scoring")
            # Generate a random score between 0.5 and 0.9 for fallback
            import random
            overall_score = random.uniform(0.5, 0.9)
        else:
            # Extract sections from resume and JD
            resume_sections = extract_resume_sections(resume_text)
            jd_sections = extract_jd_sections(jd_text)
            
            # Compute overall similarity score using LLM
            overall_score = compute_similarity_score_llm(
                chat_client, 
                resume_sections["full"], 
                jd_sections["full"]
            )
        
        # Store the score in state
        state["relevance_score"] = overall_score
        logger.info(f"Resume analysis complete. Overall relevance score: {overall_score}")
        
        # Save snapshot of the state after analysis
        save_snapshot(state)
        
        return state
    except Exception as e:
        logger.error(f"Error in resume analysis: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Add error to state
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "step": "resume_analyzer",
            "error": str(e)
        })
        return state

import traceback  # Add this import at the top with other imports

def load_resume(file_path: str) -> str:
    """Load and extract text from a resume file"""
    if not os.path.exists(file_path):
        logger.error(f"Resume file not found: {file_path}")
        return ""
    
    try:
        # Get appropriate parser based on file type
        parser = get_parser(file_path)
        
        # Extract text from the file
        text = parser.extract_text(file_path)
        
        if not text:
            logger.warning(f"Extracted empty text from {file_path}")
        else:
            logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
            
        return text
    except Exception as e:
        logger.error(f"Error loading resume {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return ""

def extract_resume_details(resume_text: str) -> Dict[str, Any]:
    """Extract details from resume text"""
    if not resume_text:
        logger.warning("Empty resume text provided for extraction")
        return {}
    
    try:
        # Extract basic information from resume text
        return extract_basic_info(resume_text)
    except Exception as e:
        logger.error(f"Error extracting resume details: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def save_snapshot(state: Dict[str, Any]) -> None:
    """Save a snapshot of the state to a JSON file for dashboard access"""
    try:
        job_id = state.get("job_id")
        if not job_id:
            logger.warning("No job ID found in state, cannot save snapshot")
            return
        
        # Create a timestamped snapshot filename
        timestamp = time.strftime("%Y%m%d%H%M%S")
        snapshot_dir = os.path.join(settings.LOG_DIR, "snapshots")
        os.makedirs(snapshot_dir, exist_ok=True)
        
        snapshot_path = os.path.join(snapshot_dir, f"{timestamp}_{job_id}_after_resume_analyzer.json")
        
        # Also save a JSON version of the resume in the incoming_resumes folder for the dashboard
        resume_json_path = None
        if "resume_path" in state:
            resume_path = state.get("resume_path")
            if resume_path and os.path.exists(resume_path):
                resume_json_path = resume_path + ".json"
        
        # Create a clean version of state for saving
        save_state = {
            "job_id": job_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "status": state.get("status", "unknown"),
            "resume_path": state.get("resume_path", ""),
            "errors": state.get("errors", []),
        }
        
        # Add resume text if available
        if "resume_text" in state:
            save_state["resume_text"] = state["resume_text"]
        
        # Add resume data if available
        if "resume_data" in state:
            save_state["resume_data"] = state["resume_data"]
        
        # Add candidate name and email if available
        if "candidate_name" in state:
            save_state["candidate_name"] = state["candidate_name"]
        
        if "candidate_email" in state:
            save_state["candidate_email"] = state["candidate_email"]
        
        # Add job description if available
        if "job_description_text" in state:
            save_state["job_description_text"] = state["job_description_text"]
        
        if "job_description" in state:
            save_state["job_description"] = state["job_description"]
        
        # Add relevance score if available
        if "relevance_score" in state:
            save_state["relevance_score"] = state["relevance_score"]
        
        # Save the snapshot
        with open(snapshot_path, 'w') as f:
            json.dump(save_state, f, indent=2)
        
        logger.info(f"Saved state snapshot to {snapshot_path}")
        
        # If we have a resume path, also save a JSON version in the incoming_resumes folder
        if resume_json_path:
            # For the resume JSON file, create a stripped down version with just what the dashboard needs
            resume_json = {
                "job_id": job_id,
                "name": save_state.get("candidate_name", "Unknown"),
                "email": save_state.get("candidate_email", ""),
                "phone": save_state.get("resume_data", {}).get("phone", ""),
                "application_date": save_state.get("timestamp", ""),
                "status": "analyzed",
                "resume_path": save_state.get("resume_path", ""),
                "relevance_score": save_state.get("relevance_score", 0),
                "skills": save_state.get("resume_data", {}).get("skills", [])
            }
            
            with open(resume_json_path, 'w') as f:
                json.dump(resume_json, f, indent=2)
            
            logger.info(f"Saved resume JSON to {resume_json_path}")
        
    except Exception as e:
        logger.error(f"Error saving state snapshot: {str(e)}")
        logger.error(traceback.format_exc())