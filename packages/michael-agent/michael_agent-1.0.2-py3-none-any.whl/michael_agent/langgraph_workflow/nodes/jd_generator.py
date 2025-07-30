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
    if state.get("job_description") and state.get("job_description_text"):
        logger.info("Job description already exists, skipping generation")
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
        
        # Generate the prompt
        prompt = get_jd_prompt(job_data)
        
        # Invoke the language model
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # Update the state with the generated job description
        state["job_description"] = job_data
        state["job_description_text"] = generated_text
        state["status"] = "jd_generated"
        
        logger.info("Job description generated successfully")
        
    except Exception as e:
        error_message = f"Error generating job description: {str(e)}"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "jd_generator",
            "error": error_message
        })
        
        # Set fallback job description text if needed
        if not state.get("job_description_text"):
            state["job_description_text"] = "Default job description text for fallback purposes."
    
    return state
