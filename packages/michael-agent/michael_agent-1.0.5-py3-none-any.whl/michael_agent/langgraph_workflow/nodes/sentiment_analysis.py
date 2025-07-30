"""
Sentiment Analysis Node
Analyzes cover letters for sentiment using Azure OpenAI
"""

import os
import logging
from typing import Dict, Any, List, Optional
import json

# Try to import Azure OpenAI
try:
    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
    from langchain_core.messages import HumanMessage
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_azure_openai_client():
    """Create and configure the Azure OpenAI client"""
    if not OPENAI_AVAILABLE:
        logger.warning("Azure OpenAI not available. Install with 'pip install langchain-openai'")
        return None
    
    try:
        # Use the correct parameter names for Azure OpenAI
        api_key = settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY or settings.OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT or settings.OPENAI_API_BASE
        api_version = settings.AZURE_OPENAI_API_VERSION or settings.OPENAI_API_VERSION
        deployment = settings.AZURE_OPENAI_DEPLOYMENT
        
        return AzureChatOpenAI(
            azure_deployment=deployment,  # Use azure_deployment parameter
            api_version=api_version,
            azure_endpoint=endpoint,  # Use azure_endpoint instead of openai_api_base
            api_key=api_key
        )
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
        return None

def create_embeddings_client():
    """
    This function is no longer used as we've removed the embedding-based approach.
    It's kept for backward compatibility but now returns None.
    """
    logger.info("Embeddings client creation skipped - using direct LLM approach instead")
    return None

def extract_cover_letter(resume_text: str) -> Optional[str]:
    """Extract cover letter text from resume text"""
    # This is a very basic implementation - in practice, you'd need more sophisticated logic
    
    # Look for "cover letter" or "letter of interest" in the text
    lines = resume_text.lower().split('\n')
    cover_letter_text = None
    
    for i, line in enumerate(lines):
        if "cover letter" in line or "letter of interest" in line or "dear hiring" in line:
            # Extract next 20 lines as the potential cover letter
            potential_cover_letter = "\n".join(lines[i:i+20])
            if len(potential_cover_letter) > 100:  # Only use if it's substantial
                cover_letter_text = potential_cover_letter
                break
    
    return cover_letter_text

def analyze_text_sentiment_openai_chat(client, text: str, screening_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze text sentiment using Azure OpenAI Chat
    Args:
        client: Azure OpenAI client
        text: Text to analyze
        screening_data: Dictionary containing screening questions and answers for additional context
    Returns:
        Sentiment analysis result
    """
    try:
        # Create the base prompt
        base_prompt = f"""
        Analyze the sentiment of the following text.
        """
        
        # Add screening questions and answers context if available
        screening_context = ""
        if screening_data and 'questions' in screening_data and 'answers' in screening_data:
            screening_context = "\n\nCandidate's screening question responses:\n"
            for i, (q, a) in enumerate(zip(screening_data['questions'], screening_data['answers'])):
                screening_context += f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n\n"
            base_prompt += f"\nConsider the following screening question responses as additional context for sentiment analysis:{screening_context}"
        
        # Complete the prompt
        prompt = base_prompt + f"""
        Respond with a JSON object containing:
        - sentiment: either "positive", "neutral", or "negative"
        - positive_score: a float between 0 and 1
        - neutral_score: a float between 0 and 1
        - negative_score: a float between 0 and 1
        - sentences: the number of sentences in the text
        
        Here's the text to analyze:
        
        {text}
        """
        
        # Get the response from Azure OpenAI
        response = client.invoke([HumanMessage(content=prompt)])
        
        # Parse the response as JSON
        try:
            content = response.content
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in content and "```" in content:
                json_part = content.split("```json")[1].split("```")[0].strip()
                sentiment_data = json.loads(json_part)
            else:
                sentiment_data = json.loads(content)
        except json.JSONDecodeError:
            # If response is not valid JSON, extract key values using simple parsing
            content = response.content.lower()
            sentiment = "positive" if "positive" in content else "negative" if "negative" in content else "neutral"
            return {
                "sentiment": sentiment,
                "positive_score": 0.33,
                "neutral_score": 0.34,
                "negative_score": 0.33,
                "sentences": len(text.split('.')),
                "parsing_method": "fallback"
            }
        
        return {
            "sentiment": sentiment_data.get("sentiment", "neutral"),
            "positive_score": sentiment_data.get("positive_score", 0.33),
            "neutral_score": sentiment_data.get("neutral_score", 0.34),
            "negative_score": sentiment_data.get("negative_score", 0.33),
            "sentences": sentiment_data.get("sentences", len(text.split('.'))),
            "parsing_method": "json"
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment with Azure OpenAI Chat: {str(e)}")
        return {
            "sentiment": "neutral",
            "positive_score": 0.33,
            "neutral_score": 0.34,
            "negative_score": 0.33,
            "sentences": len(text.split('.')),
            "error": str(e),
        }

def analyze_text_sentiment_embeddings(client, text: str) -> Dict[str, Any]:
    """
    This function is kept for backward compatibility but redirects to using the chat-based sentiment analysis
    as we've removed the embedding approach
    """
    logger.info("Embeddings-based sentiment analysis has been removed, using chat-based analysis instead")
    
    # Try to get a chat client and use that instead
    chat_client = create_azure_openai_client()
    if chat_client:
        return analyze_text_sentiment_openai_chat(chat_client, text)
    else:
        # Fall back to basic analysis if chat client creation fails
        return analyze_text_sentiment_basic(text)

def analyze_text_sentiment_basic(text: str) -> Dict[str, Any]:
    """Basic sentiment analysis without Azure services"""
    # This is a very simplified sentiment analysis - in practice, use a proper NLP library
    positive_words = ['excellent', 'good', 'great', 'best', 'outstanding', 'impressive', 
                      'excited', 'passion', 'enthusiastic', 'enjoy', 'love', 'interested', 
                      'committed', 'dedicated', 'eager']
    
    negative_words = ['unfortunately', 'bad', 'worst', 'poor', 'difficult', 'challenge', 
                      'issue', 'problem', 'concern', 'disappointed', 'regret', 'sorry']
    
    text_lower = text.lower()
    
    # Count occurrences of positive and negative words
    positive_count = sum(text_lower.count(word) for word in positive_words)
    negative_count = sum(text_lower.count(word) for word in negative_words)
    total = positive_count + negative_count
    
    # Calculate sentiment scores
    if total == 0:
        return {
            "sentiment": "neutral",
            "positive_score": 0.33,
            "neutral_score": 0.34,
            "negative_score": 0.33,
            "sentences": len(text.split('.')),
            "method": "basic"
        }
    
    positive_score = positive_count / total if total > 0 else 0.33
    negative_score = negative_count / total if total > 0 else 0.33
    neutral_score = 1 - (positive_score + negative_score)
    
    # Determine sentiment
    if positive_score > 0.6:
        sentiment = "positive"
    elif negative_score > 0.6:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "positive_score": positive_score,
        "neutral_score": neutral_score,
        "negative_score": negative_score,
        "sentences": len(text.split('.')),
        "method": "basic"
    }

def analyze_sentiment(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to analyze sentiment of cover letters using Azure OpenAI
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated workflow state with sentiment analysis
    """
    logger.info("Starting sentiment analysis with Azure OpenAI")
    
    # Initialize errors list if not present
    if "errors" not in state:
        state["errors"] = []
    
    # Check if sentiment score already exists in state
    if state.get("sentiment_score") is not None:
        logger.info("Sentiment already analyzed, skipping analysis")
        return state
    
    # Check if resume text exists
    resume_text = state.get("resume_text")
    if not resume_text:
        error_message = "Missing resume text for sentiment analysis"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "sentiment_analysis",
            "error": error_message
        })
        
        # Set default sentiment
        state["sentiment_score"] = {
            "sentiment": "neutral",
            "positive_score": 0.33,
            "neutral_score": 0.34,
            "negative_score": 0.33,
            "available": False
        }
        return state
    
    try:
        # Extract cover letter
        cover_letter = extract_cover_letter(resume_text)
        
        # If no cover letter found, use the first 1000 characters of resume as a sample
        sample_text = cover_letter if cover_letter else resume_text[:1000]
        
        # Prepare screening data if available
        screening_data = None
        if state.get("screening_questions") and state.get("screening_answers"):
            screening_data = {
                "questions": state.get("screening_questions"),
                "answers": state.get("screening_answers")
            }
        logger.info(f"Screening data prepared: {screening_data}")
        
        # Initialize clients and results
        sentiment_result = None
        chat_client = None
        
        # Try to create Azure OpenAI client for chat if available
        if OPENAI_AVAILABLE and (settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY):
            chat_client = create_azure_openai_client()
            # We no longer use embeddings, so don't initialize that client
        
        # Only use chat-based or basic sentiment analysis
        if chat_client:
            # Method 1: Use Azure OpenAI Chat for sentiment analysis
            sentiment_result = analyze_text_sentiment_openai_chat(chat_client, sample_text, screening_data)
            logger.info("Used Azure OpenAI Chat for sentiment analysis")
        else:
            # Fallback: Basic sentiment analysis
            sentiment_result = analyze_text_sentiment_basic(sample_text)
            logger.info("Used basic sentiment analysis (Azure services unavailable)")
        
        # Add additional context
        sentiment_result["cover_letter_available"] = True if cover_letter else False
        sentiment_result["text_used"] = "cover_letter" if cover_letter else "resume_sample"
        sentiment_result["available"] = True
        sentiment_result["screening_data_used"] = screening_data is not None
        
        # Update state
        state["sentiment_score"] = sentiment_result
        state["status"] = "sentiment_analyzed"
        
        logger.info(f"Sentiment analyzed successfully: {sentiment_result['sentiment']}")
        
    except Exception as e:
        error_message = f"Error analyzing sentiment: {str(e)}"
        logger.error(error_message)
        
        # Add error to state
        state["errors"].append({
            "step": "sentiment_analysis",
            "error": error_message
        })
        
        # Set default sentiment
        state["sentiment_score"] = {
            "sentiment": "neutral",
            "positive_score": 0.33,
            "neutral_score": 0.34,
            "negative_score": 0.33,
            "available": False,
            "error": str(e)
        }
    
    return state