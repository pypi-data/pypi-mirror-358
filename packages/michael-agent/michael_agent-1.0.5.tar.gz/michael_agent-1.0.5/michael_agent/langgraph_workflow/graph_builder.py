"""
LangGraph workflow builder and orchestrator
"""

import os
import json
import logging
import sys
import traceback
from typing import Dict, List, Any, Optional, TypedDict, Literal
from datetime import datetime


# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

# Import nodes (workflow steps)
from .nodes.jd_generator import generate_job_description
from .nodes.jd_poster import post_job_description
from .nodes.resume_ingestor import ingest_resume
from .nodes.resume_analyzer import analyze_resume
from .nodes.sentiment_analysis import analyze_sentiment
from .nodes.assessment_handler import handle_assessment
from .nodes.question_generator import generate_interview_questions
from .nodes.recruiter_notifier import notify_recruiter

# Import config
from config import settings

# Import custom logging utilities
from utils.logging_utils import workflow_logger as logger
from utils.logging_utils import save_state_snapshot

# Define helper function to get project root
def get_project_root():
    """Get the absolute path to the project root directory"""
    # Assuming this file is in project_root/smart_recruit_agent/langgraph_workflow/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, "../.."))

# Define the workflow state
class WorkflowState(TypedDict):
    """Type definition for the workflow state that gets passed between nodes"""
    job_id: str
    timestamp: str
    status: str
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    resume_path: Optional[str]
    resume_text: Optional[str]
    resume_data: Optional[Dict[str, Any]]
    job_description: Optional[Dict[str, Any]]
    job_description_text: Optional[str]
    relevance_score: Optional[float]
    sentiment_score: Optional[Dict[str, Any]]
    assessment: Optional[Dict[str, Any]]
    interview_questions: Optional[List[Dict[str, Any]]]
    notification_status: Optional[Dict[str, Any]]
    errors: List[Dict[str, Any]]

def create_initial_state(resume_path: str = None, job_id: str = None) -> Dict[str, Any]:
    """Create initial state for the workflow"""
    
    # If no job_id is provided, use timestamp
    if not job_id:
        # Create a timestamp-based job ID instead of UUID
        job_id = datetime.now().strftime('%Y%m%d%H%M%S')
    
    logger.info(f"Creating initial state with job ID: {job_id}")
    
    # Create initial state
    initial_state = {
        "job_id": job_id,
        "status": "initialized",
        "timestamp": datetime.now().isoformat(),
        "errors": []
    }
    
    # Add resume path if provided
    if resume_path:
        initial_state["resume_path"] = resume_path
        
    return initial_state

def should_send_assessment(state: WorkflowState) -> Literal["send_assessment", "skip_assessment"]:
    """Conditional routing to determine if assessment should be sent"""
    # Log the decision point
    logger.info(f"[Job {state.get('job_id')}] Evaluating whether to send assessment")
    
    # Check if automatic assessment sending is enabled
    if not settings.AUTOMATIC_TEST_SENDING:
        logger.info(f"[Job {state.get('job_id')}] Automatic assessment sending is disabled")
        return "skip_assessment"
    
    # Check if candidate email is available
    if not state.get("candidate_email"):
        logger.warning(f"[Job {state.get('job_id')}] No candidate email available for sending assessment")
        return "skip_assessment"
    
    # Check if score meets threshold
    score = state.get("relevance_score", 0)
    if score is None or score < settings.MINIMAL_SCORE_THRESHOLD:
        logger.info(f"[Job {state.get('job_id')}] Score {score} below threshold {settings.MINIMAL_SCORE_THRESHOLD}, skipping assessment")
        return "skip_assessment"
    
    logger.info(f"[Job {state.get('job_id')}] Assessment will be sent to {state.get('candidate_email')}")
    return "send_assessment"

def should_notify_recruiter(state: WorkflowState) -> Literal["notify", "end"]:
    """Conditional routing to determine if recruiter should be notified"""
    # Log the decision point
    logger.info(f"[Job {state.get('job_id')}] Evaluating whether to notify recruiter")
    
    # Check if automatic notification is enabled
    if not settings.AUTOMATIC_RECRUITER_NOTIFICATION:
        logger.info(f"[Job {state.get('job_id')}] Automatic recruiter notification is disabled")
        return "end"
    
    # Check if we have resume data to send
    if not state.get("resume_data"):
        error_msg = "No resume data available for notification"
        logger.warning(f"[Job {state.get('job_id')}] {error_msg}")
        state["errors"].append({
            "step": "notification_routing", 
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        return "end"
    
    logger.info(f"[Job {state.get('job_id')}] Recruiter will be notified about candidate {state.get('candidate_name')}")
    return "notify"

def build_workflow() -> StateGraph:
    """Build the LangGraph workflow"""
    # Create a new workflow graph
    logger.info("Building LangGraph workflow")
    workflow = StateGraph(WorkflowState)
    
    # Add nodes (workflow steps)
    workflow.add_node("jd_generator", generate_job_description)
    workflow.add_node("jd_poster", post_job_description)
    workflow.add_node("resume_ingestor", ingest_resume)
    workflow.add_node("resume_analyzer", analyze_resume)
    workflow.add_node("sentiment_analysis", analyze_sentiment)
    workflow.add_node("assessment_handler", handle_assessment)
    workflow.add_node("question_generator", generate_interview_questions)
    workflow.add_node("recruiter_notifier", notify_recruiter)
    
    # Define the workflow edges (flow)
    logger.debug("Defining workflow edges")
    workflow.add_edge("jd_generator", "jd_poster")
    workflow.add_edge("jd_poster", "resume_ingestor")
    workflow.add_edge("resume_ingestor", "resume_analyzer")
    workflow.add_edge("resume_analyzer", "sentiment_analysis")
    
    # After sentiment analysis, decide whether to send assessment
    workflow.add_conditional_edges(
        "sentiment_analysis",
        should_send_assessment,
        {
            "send_assessment": "assessment_handler",
            "skip_assessment": "question_generator"
        }
    )
    
    workflow.add_edge("assessment_handler", "question_generator")
    
    # After question generation, decide whether to notify recruiter
    workflow.add_conditional_edges(
        "question_generator",
        should_notify_recruiter,
        {
            "notify": "recruiter_notifier",
            "end": END
        }
    )
    
    workflow.add_edge("recruiter_notifier", END)
    
    # Replace the multiple entry points with a conditional router

    def workflow_entry_router(state: WorkflowState) -> Dict[str, Any]:
        """Route to the appropriate entry point based on available data"""
        logger.info(f"[Job {state.get('job_id')}] Routing workflow to appropriate entry point")
        
        # Create a copy of the state to avoid mutating the input
        new_state = state.copy()
        
        if state.get("resume_path") and not state.get("job_description"):
            logger.info(f"[Job {state.get('job_id')}] Starting with resume processing")
            new_state["entry_router"] = "resume_ingestor"
        elif state.get("job_description") and not state.get("resume_path"):
            logger.info(f"[Job {state.get('job_id')}] Starting with job description")
            new_state["entry_router"] = "jd_generator"
        elif state.get("resume_text") and not state.get("resume_data"):
            logger.info(f"[Job {state.get('job_id')}] Starting with resume analysis")
            new_state["entry_router"] = "resume_analyzer"
        else:
            # Default path
            logger.info(f"[Job {state.get('job_id')}] Using default entry point (job description generator)")
            new_state["entry_router"] = "jd_generator"
            
        return new_state

    # Replace the multiple START edges with a single entry and conditional router
    workflow.add_node("entry_router", workflow_entry_router)
    from langgraph.graph import START
    workflow.add_edge(START, "entry_router")
    workflow.add_conditional_edges(
        "entry_router",
        lambda x: x["entry_router"],
        {
            "jd_generator": "jd_generator",
            "resume_ingestor": "resume_ingestor",
            "resume_analyzer": "resume_analyzer"
        }
    )
    
    logger.info("Workflow graph built successfully")
    return workflow

def start_workflow():
    """Start the LangGraph workflow"""
    try:
        # Create all required directories
        for directory in [
            settings.RESUME_WATCH_DIR,
            settings.OUTPUT_DIR,
            settings.LOG_DIR,
            settings.LANGGRAPH_CHECKPOINT_DIR,
            os.path.join(settings.LOG_DIR, "snapshots")
        ]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
        
        # Build the workflow graph
        workflow = build_workflow()
        
        # Setup in-memory checkpointer
        checkpointer = InMemorySaver()
        
        # Compile the workflow
        logger.info("Compiling workflow graph")
        app = workflow.compile(checkpointer=checkpointer)
        
        # Setup the file watcher to automatically process new resumes
        logger.info("Setting up resume watcher...")
        state = create_initial_state()  # Use proper initial state type
        
        # Set up the resume watcher without running the job description generator
        # We're just initializing the watcher functionality
        try:
            # Call ingest_resume with a special flag to indicate it's just for setup
            state["setup_only"] = True
            ingest_resume(state)  # This sets up the watcher
            logger.info("Resume watcher set up successfully")
        except Exception as e:
            logger.error(f"Error setting up resume watcher: {str(e)}")
            # Continue anyway - we still want to return the app
        
        logger.info("Workflow engine successfully started")
        logger.info("Listening for new resumes...")
        
        return app
    except Exception as e:
        logger.error(f"Failed to start workflow engine: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def process_new_resume(resume_path, job_id=None):
    """Process a new resume through the workflow"""
    try:
        # Extract job ID from filename (e.g., 20250626225207_Michael_Jone.pdf)
        filename = os.path.basename(resume_path)
        job_id = filename.split('_')[0]
        logger.info(f"Extracted job ID from resume filename: {job_id}")
        
        # Create initial state with extracted job ID
        initial_state = create_initial_state(resume_path=resume_path, job_id=job_id)
        
        # Check for metadata file with screening questions/answers
        metadata_path = f"{resume_path}.json"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    
                    # Extract screening questions and answers
                    if 'screening_questions' in metadata and 'screening_answers' in metadata:
                        logger.info(f"Found screening questions/answers for resume {resume_path}")
                        initial_state['screening_questions'] = metadata['screening_questions']
                        initial_state['screening_answers'] = metadata['screening_answers']
                        
                    # Also extract candidate name and email if available
                    if 'name' in metadata:
                        initial_state['candidate_name'] = metadata['name']
                    if 'email' in metadata:
                        initial_state['candidate_email'] = metadata['email']
                    
            except Exception as e:
                logger.error(f"Error loading metadata file: {str(e)}")
        
        # Start workflow with initial state
        workflow = build_workflow()
        logger.info(f"[Job {job_id}] Starting workflow processing with job ID {job_id}")
        save_state_snapshot(initial_state, "initial_state")
        
        # Configure the workflow with in-memory checkpoints
        checkpointer = InMemorySaver()
        
        # Compile the workflow with checkpoints
        logger.info(f"[Job {job_id}] Compiling workflow graph")
        app = workflow.compile(checkpointer=checkpointer)
        
        # Execute the workflow
        try:
            logger.info(f"[Job {job_id}] Beginning workflow execution")
            event_count = 0
            
            # Add thread_id for proper checkpointing
            config = {"configurable": {"thread_id": job_id}}
            
            # Correctly process the stream events
            for event in app.stream(initial_state, config=config):
                event_count += 1
                
                # Extract the current step from the event
                # The event format depends on LangGraph version, but typically 
                # contains the node name as a key
                if isinstance(event, dict) and len(event) > 0:
                    current_step = list(event.keys())[0]
                else:
                    current_step = "unknown"
                
                # Get the current state if available in the event
                current_state = None
                if current_step in event and isinstance(event[current_step], dict):
                    current_state = event[current_step]
                    
                    # Save state snapshot after each significant step
                    if current_state:
                        save_state_snapshot(current_state, f"after_{current_step}")
                        
                        # Update status in state if possible
                        if "status" in current_state:
                            current_state["status"] = f"completed_{current_step}"
                
                # Log progress with job id for tracking
                logger.info(f"[Job {job_id}] Step {event_count} completed: {current_step}")
                
        except Exception as e:
            logger.error(f"[Job {job_id}] Error in workflow execution: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Create error state for logging
            error_state = {**initial_state}
            if "errors" not in error_state:
                error_state["errors"] = []
                
            error_state["errors"].append({
                "step": "workflow_execution",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            error_state["status"] = "workflow_execution_error"
            save_state_snapshot(error_state, "workflow_error")
    
        logger.info(f"[Job {job_id}] Workflow completed for resume {resume_path}")
    except Exception as e:
        logger.error(f"Failed to process new resume {resume_path}: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    
if __name__ == "__main__":
    # For testing the workflow directly
    start_workflow()
