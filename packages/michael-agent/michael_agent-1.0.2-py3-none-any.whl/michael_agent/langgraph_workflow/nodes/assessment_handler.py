"""
Assessment Handler Node
Sends assessments to candidates via email or LMS integration
"""

import logging
from typing import Dict, Any, List

from utils.email_utils import send_email
from utils.lms_api import get_lms_client

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_assessment_email(candidate_name: str, position_name: str, test_link: str) -> Dict[str, str]:
    """Create email content for assessment"""
    subject = f"Assessment for {position_name} Position"
    
    plain_text = f"""
    Hello {candidate_name},
    
    Thank you for your interest in the {position_name} position. As part of our evaluation process, 
    we'd like you to complete an assessment.
    
    Please click the link below to start the assessment:
    {test_link}
    
    The assessment should take approximately 60 minutes to complete.
    
    Best regards,
    Recruitment Team
    """
    
    html_content = f"""
    <html>
    <body>
        <p>Hello {candidate_name},</p>
        <p>Thank you for your interest in the <strong>{position_name}</strong> position. As part of our evaluation process, 
        we'd like you to complete an assessment.</p>
        <p>Please click the link below to start the assessment:</p>
        <p><a href="{test_link}">{test_link}</a></p>
        <p>The assessment should take approximately 60 minutes to complete.</p>
        <p>Best regards,<br>Recruitment Team</p>
    </body>
    </html>
    """
    
    return {
        "subject": subject,
        "plain_text": plain_text,
        "html_content": html_content
    }

def handle_assessment(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to handle sending assessments to candidates
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated workflow state with assessment status
    """
    logger.info("Starting assessment handler")
    
    # Check if candidate email exists in state
    candidate_email = state.get("candidate_email")
    candidate_name = state.get("candidate_name", "Candidate")
    
    if not candidate_email:
        error_message = "Missing candidate email for assessment"
        logger.error(error_message)
        state["errors"].append({
            "step": "assessment_handler",
            "error": error_message
        })
        state["assessment"] = {"status": "failed", "reason": "missing_email"}
        return state
    
    # Get job position name
    job_data = state.get("job_description", {})
    position_name = job_data.get("position", "open position")
    
    try:
        # Check if we should use LMS integration
        if settings.LMS_API_URL and settings.LMS_API_KEY:
            # Send assessment via LMS
            lms_client = get_lms_client()
            lms_result = lms_client.send_assessment(
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                position_name=position_name
            )
            
            if lms_result.get("success"):
                state["assessment"] = {
                    "status": "sent",
                    "method": "lms",
                    "lms_type": settings.LMS_TYPE,
                    "assessment_id": lms_result.get("assessment_id"),
                    "invitation_id": lms_result.get("invitation_id")
                }
                logger.info(f"Assessment sent to {candidate_email} via LMS")
            else:
                # LMS failed, fall back to email
                logger.warning(f"LMS assessment failed: {lms_result.get('error')}, falling back to email")
                assessment_link = f"https://example.com/assessment?id={state['job_id']}"
                email_content = create_assessment_email(candidate_name, position_name, assessment_link)
                
                email_sent = send_email(
                    recipient_email=candidate_email, 
                    subject=email_content["subject"],
                    body=email_content["plain_text"],
                    html_content=email_content["html_content"]
                )
                
                state["assessment"] = {
                    "status": "sent" if email_sent else "failed",
                    "method": "email",
                    "assessment_link": assessment_link
                }
                
                if email_sent:
                    logger.info(f"Assessment email sent to {candidate_email}")
                else:
                    logger.error(f"Failed to send assessment email to {candidate_email}")
                    state["errors"].append({
                        "step": "assessment_handler",
                        "error": "Failed to send assessment email"
                    })
        else:
            # No LMS configured, send via email
            assessment_link = f"https://example.com/assessment?id={state['job_id']}"
            email_content = create_assessment_email(candidate_name, position_name, assessment_link)
            
            email_sent = send_email(
                recipient_email=candidate_email, 
                subject=email_content["subject"],
                body=email_content["plain_text"],
                html_content=email_content["html_content"]
            )
            
            state["assessment"] = {
                "status": "sent" if email_sent else "failed",
                "method": "email",
                "assessment_link": assessment_link
            }
            
            if email_sent:
                logger.info(f"Assessment email sent to {candidate_email}")
            else:
                logger.error(f"Failed to send assessment email to {candidate_email}")
                state["errors"].append({
                    "step": "assessment_handler",
                    "error": "Failed to send assessment email"
                })
        
        state["status"] = "assessment_handled"
        
    except Exception as e:
        error_message = f"Error sending assessment: {str(e)}"
        logger.error(error_message)
        
        state["errors"].append({
            "step": "assessment_handler",
            "error": error_message
        })
        
        state["assessment"] = {
            "status": "failed",
            "reason": str(e)
        }
    
    return state