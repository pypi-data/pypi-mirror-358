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
from .config import settings

# Import our logging utilities early to set up logging
from .utils.logging_utils import workflow_logger as logger

def ensure_directories():
    """Ensure all required directories exist"""
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
    
    # Import node tracer after directories are created
    from .utils import node_tracer

def start_langgraph():
    """Start the LangGraph workflow in a separate thread"""
    try:
        from .langgraph_workflow.graph_builder import start_workflow
        logger.info("Starting LangGraph workflow engine...")
        langgraph_app = start_workflow()
        
        # Keep the thread alive with a simple loop
        while True:
            time.sleep(10)
    except Exception as e:
        logger.error(f"Error starting LangGraph workflow: {str(e)}")
        logger.error(traceback.format_exc())

def start_flask_dashboard():
    """Start the Flask dashboard in a separate thread"""
    try:
        from .dashboard.app import app, socketio
        port = int(os.getenv("FLASK_PORT", 5000))
        logger.info(f"Starting Flask dashboard on port {port}...")
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Error starting Flask dashboard: {str(e)}")
        logger.error(traceback.format_exc())

def main():
    """Main entry point for the application"""
    logger.info("=" * 50)
    logger.info("🚀 Starting SmartRecruitAgent")
    logger.info(f"Date/Time: {datetime.now().isoformat()}")
    logger.info("=" * 50)

    ensure_directories()
    
    port = int(os.getenv("FLASK_PORT", 5000))
    logger.info(f"Dashboard will be available at: http://localhost:{port}")
    
    try:
        # Start LangGraph in a separate thread
        langgraph_thread = threading.Thread(target=start_langgraph, name="LangGraphThread")
        langgraph_thread.daemon = True
        langgraph_thread.start()

        # Give LangGraph more time to initialize
        logger.info("Waiting for LangGraph to initialize...")
        time.sleep(5)

        logger.info("LangGraph initialization complete")

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
