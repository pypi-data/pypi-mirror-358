import os
import json
import logging
from typing import Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

def load_job_description(job_id: str = None, job_file_path: str = None) -> Dict[str, Any]:
    """Load job description from file"""
    try:
        # If path is provided directly, use it
        if job_file_path and os.path.exists(job_file_path):
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
                return job_data
        
        # If job_id is provided, look for the file in job_descriptions directory
        if job_id:
            # Look only in the root job_descriptions directory
            main_path = os.path.join("job_descriptions", f"{job_id}.json")
            if os.path.exists(main_path):
                with open(main_path, 'r') as f:
                    job_data = json.load(f)
                    return job_data
            
            logger.error(f"Job description file not found for job_id {job_id} at {main_path}")
        
        logger.error("No valid job ID or file path provided")
        return None
    except Exception as e:
        logger.error(f"Error loading job description: {e}")
        return None