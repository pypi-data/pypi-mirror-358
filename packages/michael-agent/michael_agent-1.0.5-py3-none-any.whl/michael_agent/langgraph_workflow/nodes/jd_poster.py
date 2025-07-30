"""
JD Poster Node
Mock posts job descriptions to external platforms
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def mock_post_to_linkedin(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock posting a job to LinkedIn"""
    logger.info("Mocking job post to LinkedIn")
    # Simulate API call delay
    time.sleep(0.5)
    
    return {
        "platform": "LinkedIn",
        "status": "success",
        "post_id": f"li-{uuid.uuid4()}",
        "timestamp": datetime.now().isoformat()
    }

def mock_post_to_indeed(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock posting a job to Indeed"""
    logger.info("Mocking job post to Indeed")
    # Simulate API call delay
    time.sleep(0.5)
    
    return {
        "platform": "Indeed",
        "status": "success",
        "post_id": f"ind-{uuid.uuid4()}",
        "timestamp": datetime.now().isoformat()
    }

def mock_post_to_glassdoor(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock posting a job to Glassdoor"""
    logger.info("Mocking job post to Glassdoor")
    # Simulate API call delay
    time.sleep(0.5)
    
    return {
        "platform": "Glassdoor",
        "status": "success",
        "post_id": f"gd-{uuid.uuid4()}",
        "timestamp": datetime.now().isoformat()
    }

def save_job_description(job_id: str, job_data: Dict[str, Any], job_text: str) -> str:
    """Save the job description to a file"""
    # Ensure log directory exists
    job_logs_dir = settings.JOB_DESCRIPTIONS_DIR
    os.makedirs(job_logs_dir, exist_ok=True)
    
    # Generate timestamp for filename if no job_id provided
    if not job_id:
        job_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create the job description file
    file_path = os.path.join(job_logs_dir, f"{job_id}.json")
    
    # Prepare data to save
    data_to_save = {
        "job_id": job_id,
        "timestamp": datetime.now().isoformat(),
        "job_data": job_data,
        "job_description": job_text
    }
    
    # Save to file
    with open(file_path, "w") as f:
        json.dump(data_to_save, f, indent=2)
    
    logger.info(f"Job description saved to {file_path}")
    return file_path

def post_job_description(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to post job descriptions to job boards
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated workflow state with posting results
    """
    logger.info("Starting job posting")
    
    # Check if job description already exists in state
    if not state.get("job_description") or not state.get("job_description_text"):
        error_message = "No job description available for posting"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "jd_poster",
            "error": error_message
        })
        
        return state
    
    try:
        job_id = state.get("job_id", "")
        job_data = state.get("job_description", {})
        job_text = state.get("job_description_text", "")
        
        # Save job description to file
        job_file_path = save_job_description(job_id, job_data, job_text)
        
        # Ensure the file path is stored in state
        state["job_file_path"] = job_file_path
        
        # Mock post to job platforms
        posting_results = []
        
        # LinkedIn
        linkedin_result = mock_post_to_linkedin(job_data)
        posting_results.append(linkedin_result)
        
        # Indeed
        indeed_result = mock_post_to_indeed(job_data)
        posting_results.append(indeed_result)
        
        # Glassdoor
        glassdoor_result = mock_post_to_glassdoor(job_data)
        posting_results.append(glassdoor_result)
        
        # Update state with results
        state["job_posting_results"] = posting_results
        state["status"] = "job_posted"
        
        logger.info(f"Job posted successfully to {len(posting_results)} platforms")
        
    except Exception as e:
        error_message = f"Error posting job description: {str(e)}"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "jd_poster",
            "error": error_message
        })
    
    return state
