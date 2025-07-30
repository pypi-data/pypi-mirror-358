"""
Recruiter Notifier Node
Composes and sends emails to recruiters with candidate summary
"""

import logging
from typing import Dict, Any, List

from utils.email_utils import send_email
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_recruiter_email_content(state: Dict[str, Any]) -> Dict[str, str]:
    """Create email content for recruiter notification"""
    # Get data from state
    candidate_name = state.get("candidate_name", "Unknown Candidate")
    job_data = state.get("job_description", {})
    position_name = job_data.get("position", "Unspecified Position")
    relevance_score = state.get("relevance_score", 0)
    relevance_percentage = int(relevance_score * 100)
    sentiment_data = state.get("sentiment_score", {})
    sentiment = sentiment_data.get("sentiment", "neutral")
    resume_data = state.get("resume_data", {})
    
    # Format interview questions
    interview_questions = state.get("interview_questions", {})
    tech_questions = interview_questions.get("technical_questions", [])
    behavioral_questions = interview_questions.get("behavioral_questions", [])
    
    # Create email subject
    subject = f"Candidate Assessment: {candidate_name} for {position_name} ({relevance_percentage}% Match)"
    
    # Create plain text email
    plain_text = f"""
    Candidate Assessment Report
    
    Candidate: {candidate_name}
    Position: {position_name}
    Match Score: {relevance_percentage}%
    Sentiment Analysis: {sentiment.capitalize()}
    
    Resume Summary:
    - Email: {resume_data.get('email', 'Not provided')}
    - Phone: {resume_data.get('phone', 'Not provided')}
    
    Assessment Status: {state.get('assessment', {}).get('status', 'Not sent')}
    
    Recommended Technical Interview Questions:
    {_format_questions_text(tech_questions[:3])}
    
    Recommended Behavioral Questions:
    {_format_questions_text(behavioral_questions[:3])}
    
    View the full candidate profile in the dashboard.
    """
    
    # Create HTML email content
    sentiment_color = {
        "positive": "green",
        "neutral": "gray",
        "negative": "orange"
    }.get(sentiment, "gray")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Candidate Assessment Report</h1>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="padding: 8px; width: 30%;"><strong>Candidate:</strong></td>
                    <td style="padding: 8px;">{candidate_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Position:</strong></td>
                    <td style="padding: 8px;">{position_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Match Score:</strong></td>
                    <td style="padding: 8px;">
                        <div style="background-color: #f0f0f0; border-radius: 10px; height: 20px; width: 200px;">
                            <div style="background-color: #3498db; border-radius: 10px; height: 20px; width: {relevance_percentage*2}px;"></div>
                        </div>
                        <span style="margin-left: 10px;">{relevance_percentage}%</span>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Sentiment:</strong></td>
                    <td style="padding: 8px; color: {sentiment_color};">{sentiment.capitalize()}</td>
                </tr>
            </table>
            
            <h2 style="color: #2c3e50;">Contact Information</h2>
            <p>
                <strong>Email:</strong> {resume_data.get('email', 'Not provided')}<br>
                <strong>Phone:</strong> {resume_data.get('phone', 'Not provided')}
            </p>
            
            <h2 style="color: #2c3e50;">Assessment Status</h2>
            <p>{state.get('assessment', {}).get('status', 'Not sent').capitalize()}</p>
            
            <h2 style="color: #2c3e50;">Recommended Interview Questions</h2>
            
            <h3>Technical Questions</h3>
            {_format_questions_html(tech_questions[:3])}
            
            <h3>Behavioral Questions</h3>
            {_format_questions_html(behavioral_questions[:3])}
            
            <p style="text-align: center; margin-top: 30px;">
                <a href="http://localhost:5000/dashboard" 
                   style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   View Full Profile in Dashboard
                </a>
            </p>
        </div>
    </body>
    </html>
    """
    
    return {
        "subject": subject,
        "plain_text": plain_text,
        "html_content": html_content
    }

def _format_questions_text(questions: List[Dict[str, str]]) -> str:
    """Format questions for plain text email"""
    result = ""
    for i, q in enumerate(questions, 1):
        result += f"{i}. {q.get('question', '')}\n"
    return result

def _format_questions_html(questions: List[Dict[str, str]]) -> str:
    """Format questions for HTML email"""
    result = "<ol>"
    for q in questions:
        purpose = q.get('purpose', '')
        difficulty = q.get('difficulty', '')
        difficulty_span = f"<span style='color: {'green' if difficulty == 'easy' else 'orange' if difficulty == 'medium' else 'red'}'>({difficulty})</span>" if difficulty else ""
        
        result += f"<li><strong>{q.get('question', '')}</strong> {difficulty_span}<br>"
        if purpose:
            result += f"<em>Purpose: {purpose}</em></li>"
    result += "</ol>"
    return result

def notify_recruiter(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to notify recruiters about candidates
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated workflow state with notification status
    """
    logger.info("Starting recruiter notification")
    
    # Check if notification already exists in state
    if state.get("notification_status"):
        logger.info("Notification already sent, skipping")
        return state
    
    # Get recruiter email from settings (or state if available)
    recruiter_email = state.get("recruiter_email", settings.DEFAULT_RECRUITER_EMAIL)
    
    if not recruiter_email:
        error_message = "Missing recruiter email for notification"
        logger.error(error_message)
        state["errors"].append({
            "step": "recruiter_notifier",
            "error": error_message
        })
        state["notification_status"] = {"status": "failed", "reason": "missing_email"}
        return state
    
    try:
        # Create email content
        email_content = create_recruiter_email_content(state)
        
        # Send email
        email_sent = send_email(
            recipient_email=recruiter_email,
            subject=email_content["subject"],
            body=email_content["plain_text"],
            html_content=email_content["html_content"]
        )
        
        if email_sent:
            state["notification_status"] = {
                "status": "sent",
                "recipient": recruiter_email,
                "timestamp": state["timestamp"]
            }
            state["status"] = "notification_sent"
            logger.info(f"Recruiter notification sent to {recruiter_email}")
        else:
            state["notification_status"] = {"status": "failed", "reason": "email_error"}
            state["errors"].append({
                "step": "recruiter_notifier",
                "error": "Failed to send email to recruiter"
            })
            logger.error(f"Failed to send notification to {recruiter_email}")
    
    except Exception as e:
        error_message = f"Error sending recruiter notification: {str(e)}"
        logger.error(error_message)
        
        state["errors"].append({
            "step": "recruiter_notifier",
            "error": error_message
        })
        
        state["notification_status"] = {
            "status": "failed",
            "reason": str(e)
        }
    
    return state