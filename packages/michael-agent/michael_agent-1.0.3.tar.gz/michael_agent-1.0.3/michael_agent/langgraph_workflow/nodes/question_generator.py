"""
Question Generator Node
Generates custom interview questions based on resume and job description
"""

import logging
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_llm():
    """Create and configure the LLM with Azure OpenAI"""
    try:
        return AzureChatOpenAI(
            temperature=0.7,  # Higher temperature for more diverse questions
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI: {str(e)}")
        return None

def get_question_generation_prompt(resume_text: str, jd_text: str, relevance_score: float) -> str:
    """Generate the prompt for interview question generation"""
    return f"""
    You are an expert technical interviewer and recruiter.
    
    Generate a set of interview questions for a candidate based on their resume and the job description.
    The questions should help assess the candidate's fit for the role.
    
    Resume:
    {resume_text[:2000]}  # Limit to avoid token limits
    
    Job Description:
    {jd_text[:1000]}
    
    The candidate's resume relevance score is {relevance_score:.2f} out of 1.0.
    
    Generate 10 questions in the following JSON format:
    ```json
    {{
        "technical_questions": [
            {{
                "question": "string",
                "difficulty": "easy|medium|hard",
                "category": "technical_skill|domain_knowledge|problem_solving",
                "purpose": "brief explanation of what this question assesses"
            }},
            // 4 more technical questions...
        ],
        "behavioral_questions": [
            {{
                "question": "string",
                "category": "teamwork|leadership|conflict_resolution|problem_solving|adaptability",
                "purpose": "brief explanation of what this question assesses"
            }},
            // 4 more behavioral questions...
        ],
        "follow_up_areas": ["Area 1", "Area 2", "Area 3"]  // Important areas to explore further based on resume gaps
    }}
    ```
    
    Focus on questions that will reveal the candidate's true abilities related to the job requirements.
    Include questions that address any potential gaps between the resume and job description.
    """

def generate_interview_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate interview questions based on resume and job description."""
    logger = logging.getLogger(__name__)
    logger.info("Starting interview question generation")
    
    resume_text = state.get("resume_text")
    job_description_text = state.get("job_description_text")
    
    # Add print statements to verify the input data
    print(f"[QUESTION_GENERATOR] Resume text available: {resume_text is not None}, length: {len(resume_text) if resume_text else 0}")
    print(f"[QUESTION_GENERATOR] Job description text available: {job_description_text is not None}, length: {len(job_description_text) if job_description_text else 0}")
    
    if job_description_text:
        print(f"[QUESTION_GENERATOR] JD First 200 chars: {job_description_text[:200]}...")
    
    # Generate some basic questions even if we're missing job description
    if not resume_text:
        logger.error("Missing resume text or job description text for question generation")
        # Generate generic questions when no data is available
        questions = {
            "technical_questions": [
                {
                    "question": "Can you describe your experience with the technologies mentioned in your resume?",
                    "difficulty": "medium",
                    "category": "technical_skill",
                    "purpose": "Assess general technical experience and honesty"
                },
                {
                    "question": "How do you approach problem-solving in your work?",
                    "difficulty": "medium",
                    "category": "problem_solving",
                    "purpose": "Evaluate general problem-solving approach"
                }
            ],
            "behavioral_questions": [
                {
                    "question": "Can you tell me about a time when you had to work with a difficult team member?",
                    "category": "teamwork",
                    "purpose": "Assess interpersonal skills and conflict resolution"
                },
                {
                    "question": "Describe a situation where you had to learn something new quickly.",
                    "category": "adaptability",
                    "purpose": "Evaluate learning agility and adaptability"
                }
            ],
            "follow_up_areas": [
                "Technical skills verification",
                "Past project details",
                "Team collaboration"
            ]
        }
        
        return {
            "status": "completed_generate_interview_questions",
            "interview_questions": questions,
            "errors": [{"step": "question_generator", "error": "Missing resume text or job description text for question generation"}]
        }
    
    # Check if questions already exist in state
    if state.get("interview_questions"):
        logger.info("Interview questions already exist, skipping generation")
        return state
    
    # Check if required data exists
    resume_text = state.get("resume_text")
    jd_text = state.get("job_description_text")
    
    if not resume_text or not jd_text:
        error_message = "Missing resume text or job description text for question generation"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "question_generator",
            "error": error_message
        })
        
        # Set default questions
        state["interview_questions"] = generate_default_questions()
        return state
    
    try:
        # Create the language model
        llm = create_llm()
        if not llm:
            raise ValueError("Failed to initialize Azure OpenAI client")
        
        # Get resume score from state (default to 0.5 if missing)
        relevance_score = state.get("relevance_score", 0.5)
        
        # Generate the prompt
        prompt = get_question_generation_prompt(resume_text, jd_text, relevance_score)
        print(f"[QUESTION_GENERATOR] Created prompt with resume length {len(resume_text)} and JD length {len(jd_text)}")
        
        # Invoke the language model
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # Extract JSON from response (in case there's surrounding text)
        import re
        import json
        
        json_match = re.search(r'```json\s*(.*?)\s*```', generated_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no markdown code block, try to find JSON directly
            json_match = re.search(r'({[\s\S]*})', generated_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("Could not extract JSON from LLM response")
                
        # Parse the JSON
        questions = json.loads(json_str)
        
        # Update the state with the generated questions
        state["interview_questions"] = questions
        state["status"] = "questions_generated"
        
        # Save a snapshot of the state with the questions
        save_snapshot(state)
        
        logger.info("Interview questions generated successfully")
        
    except Exception as e:
        error_message = f"Error generating interview questions: {str(e)}"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "question_generator",
            "error": error_message
        })
        
        # Use default questions as fallback
        state["interview_questions"] = generate_default_questions()
    
    return state

def generate_default_questions():
    """Generate default interview questions as fallback"""
    return {
        "technical_questions": [
            {
                "question": "Can you describe your experience with the technologies mentioned in your resume?",
                "difficulty": "medium",
                "category": "technical_skill",
                "purpose": "Assess general technical experience and honesty"
            },
            {
                "question": "How do you approach problem-solving in your work?",
                "difficulty": "medium",
                "category": "problem_solving",
                "purpose": "Evaluate general problem-solving approach"
            }
        ],
        "behavioral_questions": [
            {
                "question": "Can you tell me about a time when you had to work with a difficult team member?",
                "category": "teamwork",
                "purpose": "Assess interpersonal skills and conflict resolution"
            },
            {
                "question": "Describe a situation where you had to learn something new quickly.",
                "category": "adaptability",
                "purpose": "Evaluate learning agility and adaptability"
            }
        ],
        "follow_up_areas": ["Technical skills verification", "Past project details", "Team collaboration"]
    }

def save_snapshot(state: Dict[str, Any]) -> None:
    """Save a snapshot of the state to a JSON file for dashboard access"""
    try:
        import os
        import json
        import time
        
        job_id = state.get("job_id")
        if not job_id:
            logger.warning("No job ID found in state, cannot save snapshot")
            return
        
        # Create a timestamped snapshot filename
        timestamp = time.strftime("%Y%m%d%H%M%S")
        snapshot_dir = os.path.join("./logs", "snapshots")
        os.makedirs(snapshot_dir, exist_ok=True)
        
        snapshot_path = os.path.join(snapshot_dir, f"{timestamp}_{job_id}_after_question_generator.json")
        
        # Create a clean version of state for saving
        save_state = {
            "job_id": job_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "status": state.get("status", "unknown"),
            "resume_path": state.get("resume_path", ""),
            "errors": state.get("errors", []),
        }
        
        # Add candidate name and email if available
        if "candidate_name" in state:
            save_state["candidate_name"] = state["candidate_name"]
        
        if "candidate_email" in state:
            save_state["candidate_email"] = state["candidate_email"]
        
        # Add interview questions if available
        if "interview_questions" in state:
            save_state["interview_questions"] = state["interview_questions"]
        
        # Save the snapshot
        with open(snapshot_path, 'w') as f:
            json.dump(save_state, f, indent=2)
        
        logger.info(f"Saved question generator snapshot to {snapshot_path}")
        
    except Exception as e:
        logger.error(f"Error saving state snapshot: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())