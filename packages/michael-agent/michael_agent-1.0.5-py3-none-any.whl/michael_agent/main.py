#!/usr/bin/env python3
"""
SmartRecruitAgent - Main Entry Point
Starts both the LangGraph workflow and Flask dashboard concurrently
"""

import os
import threading
import time
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Then import settings which may depend on environment variables
from config import settings 

# Import our logging utilities early to set up logging
from utils.logging_utils import workflow_logger as logger

# Ensure all required directories exist
required_directories = [
    settings.RESUME_WATCH_DIR,
    settings.OUTPUT_DIR,
    settings.LOG_DIR,
    os.path.join(settings.LOG_DIR, "snapshots"),
    settings.LANGGRAPH_CHECKPOINT_DIR,
    settings.JOB_DESCRIPTIONS_DIR
]

for directory in required_directories:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

# Import our node tracer to apply logging to all workflow nodes
# This must be imported after directories are created but before the workflow starts
import utils.node_tracer
from utils.id_mapper import get_timestamp_id, get_all_ids_for_timestamp

def start_langgraph():
    """Start the LangGraph workflow in a separate thread"""
    global langgraph_app  # Add a global reference to store the app
    try:
        from langgraph_workflow.graph_builder import start_workflow
        logger.info("Starting LangGraph workflow engine...")
        langgraph_app = start_workflow()  # Store the returned app
        
        # Keep the thread alive with a simple loop
        while True:
            time.sleep(10)  # Sleep to avoid high CPU usage
    except Exception as e:
        logger.error(f"Error starting LangGraph workflow: {str(e)}")
        logger.error(traceback.format_exc())

def start_flask_dashboard():
    """Start the Flask dashboard in a separate thread"""
    try:
        from dashboard.app import app, socketio
        # Use threading instead of eventlet for the background tasks
        import threading

        # Configure Socket.IO to not use eventlet
        socketio.init_app(app, async_mode='threading')

        port = int(os.getenv("FLASK_PORT", 8080))
        logger.info(f"Starting Flask dashboard on http://localhost:{port}")
        # Start the Flask app with threading
        socketio.run(app, host='0.0.0.0', port=port, debug=os.getenv("FLASK_ENV") == "development", use_reloader=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Error starting Flask dashboard: {str(e)}")
        logger.error(traceback.format_exc())


def main():
    """Main entry point for the application"""
    logger.info("=" * 50)
    logger.info("🚀 Starting SmartRecruitAgent")
    logger.info(f"Date/Time: {datetime.now().isoformat()}")
    logger.info("=" * 50)

    port = int(os.getenv("FLASK_PORT", 8080))
    logger.info(f"Dashboard will be available at: http://localhost:{port}")
    
    try:
        # Start LangGraph in a separate thread
        langgraph_thread = threading.Thread(target=start_langgraph, name="LangGraphThread")
        langgraph_thread.daemon = True
        langgraph_thread.start()

        # Give LangGraph more time to initialize
        logger.info("Waiting for LangGraph to initialize...")
        time.sleep(5)  # Increased from 2 to 5 seconds

        logger.info("LangGraph initialization complete")

        # Verify job description directory exists and is accessible
        job_description_dir = "job_descriptions"
        os.makedirs(job_description_dir, exist_ok=True)
        logger.info(f"Job description directory verified: {job_description_dir}")

        # Start Flask dashboard in the main thread
        logger.info("Starting Flask dashboard in main thread...")
        start_flask_dashboard()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("SmartRecruitAgent shutting down...")
    
if __name__ == "__main__":
    main()

def on_created(self, event):
    """Process newly created resume files"""
    # Skip temporary files and directories
    if event.is_directory or event.src_path.endswith('.tmp'):
        return
        
    # Check if the file matches resume extensions
    file_ext = os.path.splitext(event.src_path)[1].lower()
    if file_ext not in self.valid_extensions:
        return
        
    try:
        # Create timestamped filename if needed
        filename = os.path.basename(event.src_path)
        if not self.has_timestamp_prefix(filename):
            # Add timestamp as job ID prefix
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_filename = f"{timestamp}_{filename}"
            new_path = os.path.join(os.path.dirname(event.src_path), new_filename)
            os.rename(event.src_path, new_path)
            file_path = new_path
        else:
            file_path = event.src_path
            
        logger.info(f"New resume detected: {file_path}")
        
        # Process the resume through the workflow
        self.processor_func(file_path)
    except Exception as e:
        logger.error(f"Error processing new resume {event.src_path}: {str(e)}")
        logger.error(traceback.format_exc())
    
def has_timestamp_prefix(self, filename):
    """Check if filename has a timestamp prefix in format YYYYMMDDHHMMSS_"""
    # Extract the first part before underscore
    parts = filename.split('_', 1)
    if len(parts) < 2:
        return False
        
    prefix = parts[0]
    # Check if prefix is a 14-digit number (YYYYMMDDHHMMSS)
    return len(prefix) == 14 and prefix.isdigit()
