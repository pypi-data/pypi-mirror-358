"""
Logging utilities for SmartRecruitAgent
Provides consistent logging configuration and helpers
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Callable, Optional

# Import config
from config import settings

# Configure the base logging system
def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Set up and configure a logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create the workflow logger
workflow_logger = setup_logger(
    'workflow',
    os.path.join(settings.LOG_DIR, 'workflow.log')
)

# Create the state transitions logger
state_logger = setup_logger(
    'state_transitions',
    os.path.join(settings.LOG_DIR, 'state_transitions.log')
)

def log_state_transition(before_state: Dict[str, Any], after_state: Dict[str, Any], step_name: str) -> None:
    """Log state transitions between workflow steps"""
    # Create a simplified log of what changed
    changes = {}
    
    # Track only the keys that changed
    for key in after_state:
        if key not in before_state or before_state[key] != after_state[key]:
            # For complex objects, just note they changed rather than logging entire content
            if isinstance(after_state[key], dict) or isinstance(after_state[key], list):
                changes[key] = f"{type(after_state[key]).__name__} modified"
            else:
                changes[key] = after_state[key]
    
    # Record any errors added in this step
    errors = []
    if "errors" in after_state and isinstance(after_state["errors"], list):
        before_errors_count = len(before_state.get("errors", []))
        if len(after_state["errors"]) > before_errors_count:
            errors = after_state["errors"][before_errors_count:]
    
    # Create the log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "step": step_name,
        "job_id": after_state.get("job_id", "unknown"),
        "candidate": after_state.get("candidate_name", "unknown"),
        "status": after_state.get("status", "unknown"),
        "changes": changes,
        "errors": errors
    }
    
    # Add a JSON serialization helper function
    def json_serializable(obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: json_serializable(v) for k, v in obj.items() if isinstance(k, str)}
        return str(obj)  # Convert non-serializable objects to strings
    
    # Modify the log_entry or use the helper
    serializable_log_entry = json_serializable(log_entry)
    # Log to file
    state_logger.info(json.dumps(serializable_log_entry))

def log_step(func: Callable) -> Callable:
    """Decorator for logging workflow step execution with detailed tracking"""
    @wraps(func)
    def wrapper(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        step_name = func.__name__
        job_id = state.get("job_id", "unknown")
        
        # Log step start
        workflow_logger.info(f"Starting step: {step_name} for job {job_id}")
        
        # Store the state before execution for comparison
        before_state = {**state}
        
        try:
            # Execute the step
            result_state = func(state, *args, **kwargs)
            
            # Handle case when function returns None instead of state
            if result_state is None:
                workflow_logger.debug(f"Step {step_name} returned None; using original state.")
                result_state = before_state
            
            # Update status to reflect step completion
            if isinstance(result_state, dict) and "status" in result_state:
                result_state["status"] = f"completed_{step_name}"
            
            # Log successful completion
            workflow_logger.info(f"Completed step: {step_name} for job {job_id}")
            
            # Log state transitions
            log_state_transition(before_state, result_state, step_name)
            
            return result_state
            
        except Exception as e:
            # Log the exception with traceback
            error_msg = f"Error in step {step_name}: {str(e)}"
            workflow_logger.error(error_msg)
            workflow_logger.error(traceback.format_exc())
            
            # Update state with error information
            if "errors" not in state:
                state["errors"] = []
            
            state["errors"].append({
                "step": step_name,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            if "status" in state:
                state["status"] = f"error_in_{step_name}"
            
            # Log state transition with error
            log_state_transition(before_state, state, f"{step_name}_error")
            
            return state
    
    return wrapper

def save_state_snapshot(state: Dict[str, Any], step: str) -> None:
    """Save a snapshot of the current state to a JSON file"""
    try:
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        job_id = state.get("job_id", "unknown")
        filename = f"{timestamp}_{job_id}_{step}.json"
        
        # Create the snapshots directory
        snapshots_dir = os.path.join(settings.LOG_DIR, "snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)
        
        # Create a clean copy of the state (remove any objects that can't be serialized)
        clean_state = {}
        for key, value in state.items():
            try:
                # Test if it can be serialized
                json.dumps({key: value})
                clean_state[key] = value
            except (TypeError, OverflowError):
                clean_state[key] = f"<non-serializable: {type(value).__name__}>"
        
        # Write the state to file
        with open(os.path.join(snapshots_dir, filename), 'w') as f:
            json.dump(clean_state, f, indent=2, default=str)
            
        workflow_logger.debug(f"State snapshot saved: {filename}")
    except Exception as e:
        workflow_logger.error(f"Failed to save state snapshot: {str(e)}")
