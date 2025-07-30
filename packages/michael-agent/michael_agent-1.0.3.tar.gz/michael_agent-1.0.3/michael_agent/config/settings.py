"""
SmartRecruitAgent Configuration Settings
Centralizes all configuration parameters and Azure service configurations
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("OPENAI_API_VERSION", "2023-05-15")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "ES-LMS")  # Default to ES-LMS

# Azure OpenAI Embedding Configuration
AZURE_EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-ada-002")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY") or AZURE_OPENAI_KEY
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_EMBEDDING_ENDPOINT") or AZURE_OPENAI_ENDPOINT
AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION", "2023-05-15")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
AZURE_OPENAI_API_KEY = AZURE_OPENAI_KEY

# Azure Form Recognizer Configuration
AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")

# Azure Communication Services Configuration
AZURE_COMMUNICATION_CONNECTION_STRING = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
AZURE_COMMUNICATION_SENDER_EMAIL = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL", "recruitment@example.com")

# Email SMTP Configuration (Alternative to Azure Communication Services)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "recruitment@example.com")

# LangGraph Configuration
LANGGRAPH_CHECKPOINT_DIR = os.getenv("LANGGRAPH_CHECKPOINT_DIR", "./checkpoints")

# Learning Management System API Configuration
LMS_API_URL = os.getenv("LMS_API_URL")
LMS_API_KEY = os.getenv("LMS_API_KEY")
LMS_TYPE = os.getenv("LMS_TYPE", "hackerrank")  # Options: hackerrank, testgorilla, custom

# File System Configuration - ensure these are properly set
RESUME_WATCH_DIR = os.getenv("RESUME_WATCH_DIR", "./incoming_resumes")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./processed_resumes")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
JOB_DESCRIPTIONS_DIR = os.getenv("JOB_DESCRIPTIONS_DIR", "./job_descriptions")

# Dashboard Configuration
DASHBOARD_UPDATE_INTERVAL = int(os.getenv("DASHBOARD_UPDATE_INTERVAL", 5))  # seconds

# Workflow Configuration
MINIMAL_SCORE_THRESHOLD = float(os.getenv("MINIMAL_SCORE_THRESHOLD", 0.6))  # 0.0 to 1.0
AUTOMATIC_TEST_SENDING = os.getenv("AUTOMATIC_TEST_SENDING", "false").lower() == "true"
AUTOMATIC_RECRUITER_NOTIFICATION = os.getenv("AUTOMATIC_RECRUITER_NOTIFICATION", "false").lower() == "true"
DEFAULT_RECRUITER_EMAIL = os.getenv("DEFAULT_RECRUITER_EMAIL", "recruiter@example.com")

# Job Descriptions Directory

# Note: Directory creation moved to main.py to avoid duplicate creation
