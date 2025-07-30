"""
Utility to apply logging decorators to workflow nodes
Ensures consistent logging across all workflow steps
"""

import os
import sys
import inspect
import logging
import importlib
from types import ModuleType
from typing import Dict, Any, Callable
from functools import wraps

# Import our logging decorator
from utils.logging_utils import log_step, workflow_logger as logger

def trace_node(node_function: Callable) -> Callable:
    """Apply tracing to a node function"""
    # First, apply our standard logging decorator
    traced_function = log_step(node_function)
    
    @wraps(node_function)
    def wrapper(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        # Get the job ID for logging
        job_id = state.get("job_id", "unknown")
        logger.debug(f"[Job {job_id}] Entering node {node_function.__name__}")
        
        try:
            # Call the decorated function
            result = traced_function(state, *args, **kwargs)
            return result
        except Exception as e:
            # Log the error and re-raise it (our decorator will handle it)
            logger.error(f"[Job {job_id}] Exception in {node_function.__name__}: {str(e)}")
            raise
    
    return wrapper

def trace_workflow_nodes():
    """Apply tracing to all workflow nodes"""
    # Define the base path to our nodes directory
    nodes_dir = os.path.join(os.path.dirname(__file__), '..', 'langgraph_workflow', 'nodes')
    sys.path.append(os.path.abspath(os.path.join(nodes_dir, '..')))
    
    nodes_path = 'langgraph_workflow.nodes'
    logger.info(f"Applying tracing to workflow nodes in {nodes_path}")
    
    # Get all Python files in the nodes directory (excluding __init__ and __pycache__)
    node_modules = []
    for filename in os.listdir(nodes_dir):
        if (filename.endswith('.py') and 
            filename != '__init__.py' and 
            not filename.startswith('__')):
            module_name = filename[:-3]  # Remove .py extension
            node_modules.append(module_name)
    
    # Apply tracing to node functions in each module
    for module_name in node_modules:
        full_module_name = f"{nodes_path}.{module_name}"
        try:
            # Import the module
            module = importlib.import_module(full_module_name)
            
            # Find all functions in the module that might be node functions
            traced_count = 0
            for name, obj in inspect.getmembers(module):
                if (inspect.isfunction(obj) and 
                    not name.startswith('_') and
                    'state' in inspect.signature(obj).parameters):
                    
                    # This looks like a node function, apply tracing
                    original_function = obj
                    traced_function = trace_node(original_function)
                    
                    # Replace the original function with our traced version
                    setattr(module, name, traced_function)
                    traced_count += 1
            
            logger.info(f"Applied tracing to {traced_count} functions in {full_module_name}")
            
        except Exception as e:
            logger.error(f"Error applying tracing to {full_module_name}: {str(e)}")
    
    logger.info("Tracing applied to all workflow nodes")

# Apply tracing automatically when this module is imported
trace_workflow_nodes()
