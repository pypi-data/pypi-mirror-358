"""
Resume Ingestor Node
Watches for new resumes from local directory
"""

import os
import logging
import shutil
import time
import atexit
import json
from typing import Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for watchdog observer
_global_observer = None

# Global variable for watchdog observer
_global_observer = None

class ResumeFileHandler(FileSystemEventHandler):
    """File system event handler for monitoring new resume files"""
    
    def __init__(self, callback_fn):
        self.callback_fn = callback_fn
        self.extensions = ['.pdf', '.docx', '.doc', '.txt']
        
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if any(file_path.lower().endswith(ext) for ext in self.extensions):
                logger.info(f"New resume detected: {file_path}")
                self.callback_fn(file_path)

def setup_watcher(watch_dir: str, callback_fn):
    """Set up a file system watcher for the specified directory"""
    observer = Observer()
    event_handler = ResumeFileHandler(callback_fn)
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    
    # Store in global variable for cleanup
    global _global_observer
    _global_observer = observer
    
    return observer

def copy_resume_to_output(resume_path: str) -> str:
    """Copy the resume to the output directory"""
    try:
        # Ensure output directory exists
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Copy the file to output directory
        filename = os.path.basename(resume_path)
        output_path = os.path.join(settings.OUTPUT_DIR, filename)
        shutil.copy2(resume_path, output_path)
        
        # Return the path to the copied file
        return output_path
    except Exception as e:
        logger.error(f"Error copying resume to output: {str(e)}")
        raise

def ingest_resume(state: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest new resumes for processing from the local file system"""
    try:
        # Check if this is just a setup call without processing existing files
        setup_only = state.get("setup_only", False)
        
        # Check if we already have a resume path in the state
        if state.get("resume_path") and not setup_only:
            logger.info(f"Processing resume from state: {state.get('resume_path')}")
            resume_path = state.get("resume_path")
            
            # Copy to output directory if it exists and is not already there
            if os.path.exists(resume_path) and not resume_path.startswith(settings.OUTPUT_DIR):
                output_path = copy_resume_to_output(resume_path)
                # Update the path to point to the copied file
                state["resume_path"] = output_path
                logger.info(f"Copied resume to output directory: {output_path}")
            
            # Move on with the workflow
            return state
        
        # Ensure output directory exists
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Ensure log directory exists
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        
        # Set up local file system watcher if not already running
        if 'resume_watcher' not in state or not state['resume_watcher']:
            # Create the watch directory if it doesn't exist
            os.makedirs(settings.RESUME_WATCH_DIR, exist_ok=True)
            
            # Process any existing files in the directory (skip if setup_only)
            if not setup_only:
                for filename in os.listdir(settings.RESUME_WATCH_DIR):
                    file_path = os.path.join(settings.RESUME_WATCH_DIR, filename)
                    if os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in ['.pdf', '.docx', '.doc', '.txt']) and not filename.endswith('.json'):
                        logger.info(f"Processing existing resume: {file_path}")
                        output_path = copy_resume_to_output(file_path)
                        if 'resumes' not in state:
                            state['resumes'] = []
                        state['resumes'].append({
                            'filename': os.path.basename(file_path),
                            'path': output_path,
                            'status': 'received'
                        })
                        
                        # Automatically trigger workflow for this resume
                        from langgraph_workflow.graph_builder import process_new_resume
                        try:
                            process_new_resume(file_path)
                            logger.info(f"Triggered workflow for existing resume: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to trigger workflow for existing resume {file_path}: {str(e)}")
            else:
                logger.info("Setup only mode - skipping processing of existing files")
            
            # Set up the watcher for future files
            def process_new_file(file_path):
                logger.info(f"New resume detected: {file_path}")
                output_path = copy_resume_to_output(file_path)
                # Update the state (in a real app, you'd need proper concurrency handling)
                if 'resumes' not in state:
                    state['resumes'] = []
                state['resumes'].append({
                    'filename': os.path.basename(file_path),
                    'path': output_path,
                    'status': 'received'
                })
                
                # Automatically trigger workflow for this resume, specifying resume_ingestor as the entry point
                from langgraph_workflow.graph_builder import process_new_resume
                try:
                    process_new_resume(file_path)
                    logger.info(f"Triggered workflow for new resume: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to trigger workflow for new resume {file_path}: {str(e)}")
            
            # Start the watcher
            observer = setup_watcher(settings.RESUME_WATCH_DIR, process_new_file)
            state['resume_watcher'] = observer
        
        return state
    except Exception as e:
        logger.error(f"Error in resume ingestion: {str(e)}")
        # Add error to state
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Resume ingestion error: {str(e)}")
        return state

def extract_job_id_from_filename(filename: str) -> str:
    """Extract job ID from the resume filename"""
    try:
        # Assuming the job ID is the first part of the filename, before an underscore
        job_id = os.path.basename(filename).split('_')[0]
        logger.info(f"Extracted job ID {job_id} from filename {filename}")
        return job_id
    except Exception as e:
        logger.error(f"Error extracting job ID from filename {filename}: {str(e)}")
        return ""

def process_resume(file_path: str, state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process a resume file
    """
    logger.info(f"Processing resume from state: {file_path}")
    
    # Extract job ID from filename (e.g., 20250626225207_Michael_Jone.pdf)
    try:
        job_id = extract_job_id_from_filename(file_path)
        logger.info(f"Extracted job ID from filename: {job_id}")
        
        # Update state with the extracted job ID
        if state is None:
            state = {}
        state["job_id"] = job_id
        logger.info(f"Updated state with job ID: {job_id}")
    except Exception as e:
        logger.error(f"Failed to extract job ID from filename: {e}")
    
    # Copy resume to processed directory
    output_dir = "./processed_resumes"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get just the filename without path
    filename = os.path.basename(file_path)
    output_path = os.path.join(output_dir, filename)
    
    shutil.copy(file_path, output_path)
    logger.info(f"Copied resume to output directory: {output_path}")
    
    # Return updated state with resume path and job_id
    return {
        "status": "completed_ingest_resume",
        "resume_path": output_path,
        "job_id": job_id
    }

def cleanup(state: Dict[str, Any]) -> None:
    """Clean up resources when shutting down"""
    try:
        if 'resume_watcher' in state and state['resume_watcher']:
            logger.info("Stopping resume watcher...")
            state['resume_watcher'].stop()
            state['resume_watcher'].join(timeout=5.0)  # Wait up to 5 seconds for clean shutdown
            logger.info("Resume watcher stopped")
    except Exception as e:
        logger.error(f"Error stopping resume watcher: {str(e)}")
        
# Register cleanup function to be called on program exit
import atexit
atexit.register(lambda: cleanup({'resume_watcher': globals().get('_global_observer')}))
