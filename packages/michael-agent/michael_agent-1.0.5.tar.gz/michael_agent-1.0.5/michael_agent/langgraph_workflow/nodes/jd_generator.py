"""
Job Description Generator Node
Generates detailed job descriptions using Azure OpenAI
"""

import os
import logging
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

# Import the JD creation utility (from your existing code)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_llm():
    """Create and configure the LLM with Azure OpenAI"""
    try:
        api_key = settings.AZURE_OPENAI_KEY or settings.AZURE_OPENAI_API_KEY or settings.OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT or settings.OPENAI_API_BASE
        api_version = settings.AZURE_OPENAI_API_VERSION or settings.OPENAI_API_VERSION
        
        return AzureChatOpenAI(
            temperature=0.3,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,  # Using deployment_name instead of deployment
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI: {str(e)}")
        return None

def get_jd_prompt(job_data: Dict[str, Any]) -> str:
    """Generate the prompt for job description creation"""
    position = job_data.get('position', 'Software Engineer')  # Default to Software Engineer if position not provided
    return f"""
    You are an expert HR content writer specializing in job descriptions.
    Create a comprehensive job description for a {position} role.

    Include the following sections:

    - Introduction to the role and company
    - Work tasks and responsibilities
    - Required qualifications and skills
    - Preferred skills and experience
    - Compensation and benefits information
    - About the organization
    - Application process information
    - include only the required skills and preferred skills in the job description

    Location: {job_data.get('location', 'Not specified')}
    Business area: {job_data.get('business_area', 'Not specified')}
    Employment type: {job_data.get('employment_type', 'Full-time')}
    Experience level: {job_data.get('experience_level', 'Not specified')}
    Work arrangement: {job_data.get('work_arrangement', 'Not specified')}

    Required skills: {', '.join(job_data.get('required_skills', []))}
    Preferred skills: {', '.join(job_data.get('preferred_skills', []))}

    Write in professional English, be concise yet comprehensive, and highlight the value 
    proposition for potential candidates.
    """

def get_screening_questions_prompt(job_data: Dict[str, Any]) -> str:
    """Generate the prompt for screening questions creation"""
    position = job_data.get('position', 'Software Engineer') 
    return f"""
    You are an HR specialist creating initial screening questions for job applicants.
    Create 5 simple screening questions for a {position} role.
    
    These questions should:
    1. Be simple and quick to answer (yes/no or short responses)
    2. Relate directly to the role's basic requirements
    3. Help filter candidates early in the process
    4. Be easy to understand without technical jargon
    5. Assess key role-related experience or skills
    
    Job details:
    Position: {job_data.get('position', 'Software Engineer')}
    Required skills: {', '.join(job_data.get('required_skills', []))}
    Experience level: {job_data.get('experience_level', 'Not specified')}
    
    Format your response as a JSON array with exactly 5 questions:
    [
      "Question 1",
      "Question 2",
      "Question 3", 
      "Question 4",
      "Question 5"
    ]
    """

def generate_job_description(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to generate a job description
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated workflow state with job description
    """
    logger.info("Starting job description generation")
    
    # Check if job description already exists in state
    if state.get("job_description") and state.get("job_description_text") and state.get("screening_questions"):
        logger.info("Job description and screening questions already exist, skipping generation")
        return state
    
    try:
        # Create the language model
        llm = create_llm()
        if not llm:
            raise ValueError("Failed to initialize Azure OpenAI client")
        
        # Prepare job data (use sample data if not provided)
        job_data = state.get("job_description", {})
        if not job_data:
            # Use default job data if none provided
            job_data = {
                "position": "Software Engineer",
                "location": "Remote",
                "business_area": "Engineering",
                "employment_type": "Full-time",
                "experience_level": "Mid-level",
                "work_arrangement": "Remote",
                "required_skills": ["Python", "JavaScript", "API Development"],
                "preferred_skills": ["Azure", "CI/CD", "TypeScript"]
            }
        
        # Generate the prompt for job description
        jd_prompt = get_jd_prompt(job_data)
        
        # Generate the prompt for screening questions
        sq_prompt = get_screening_questions_prompt(job_data)
        
        # Invoke the language model for job description
        jd_response = llm.invoke(jd_prompt)
        generated_jd_text = jd_response.content
        
        # Invoke the language model for screening questions
        sq_response = llm.invoke(sq_prompt)
        generated_sq_text = sq_response.content
        
        # Extract questions from the response (handling JSON format)
        screening_questions = []
        try:
            import json
            import re
            
            # Try to parse JSON directly
            try:
                screening_questions = json.loads(generated_sq_text)
            except json.JSONDecodeError:
                # Extract JSON array using regex if direct parsing fails
                json_match = re.search(r'\[\s*".*"\s*\]', generated_sq_text, re.DOTALL)
                if json_match:
                    screening_questions = json.loads(json_match.group(0))
                else:
                    # Simple line-by-line extraction as fallback
                    lines = generated_sq_text.strip().split('\n')
                    for line in lines:
                        question = line.strip().strip('"[]').strip('"').strip()
                        if question and not question.startswith('#') and not question.startswith('//'):
                            screening_questions.append(question)
        except Exception as e:
            logger.error(f"Error parsing screening questions: {str(e)}")
            # Fallback questions
            screening_questions = [
                f"Do you have experience as a {job_data.get('position', 'professional')}?",
                f"Are you familiar with {', '.join(job_data.get('required_skills', ['the required skills']))}?",
                f"Can you work in {job_data.get('location', 'this location')}?",
                f"Are you available for {job_data.get('employment_type', 'this position type')}?",
                "How many years of relevant experience do you have?"
            ]
        
        # Ensure we have exactly 5 questions
        if len(screening_questions) > 5:
            screening_questions = screening_questions[:5]
        while len(screening_questions) < 5:
            screening_questions.append(f"Do you have experience with {job_data.get('preferred_skills', ['the preferred skills'])[0] if job_data.get('preferred_skills') else 'the relevant technologies'}?")
        
        # Update the state with the generated job description and screening questions
        state["job_description"] = job_data
        state["job_description_text"] = generated_jd_text
        state["screening_questions"] = screening_questions
        state["status"] = "jd_generated"
        
        logger.info("Job description and screening questions generated successfully")
        
    except Exception as e:
        error_message = f"Error generating job description: {str(e)}"
        logger.error(error_message)
        
        # Add error to state
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "step": "jd_generator",
            "error": error_message
        })
        
        # Set fallback job description text if needed
        if not state.get("job_description_text"):
            state["job_description_text"] = "Default job description text for fallback purposes."
            
        # Set fallback screening questions if needed
        if not state.get("screening_questions"):
            state["screening_questions"] = [
                "Do you have experience with this role?",
                "Are you familiar with the required skills?",
                "Can you work in the specified location?",
                "Are you available for the listed employment type?",
                "How many years of relevant experience do you have?"
            ]
    
    return state
