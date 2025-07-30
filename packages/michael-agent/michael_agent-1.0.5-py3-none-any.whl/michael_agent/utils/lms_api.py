"""
LMS (Learning Management System) API integration utilities
Supports integration with HackerRank, TestGorilla, or custom LMS APIs
"""

import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any

from config import settings

logger = logging.getLogger(__name__)

class LMSIntegration:
    """Base class for LMS integrations"""
    
    def __init__(self):
        self.api_url = settings.LMS_API_URL
        self.api_key = settings.LMS_API_KEY
    
    def send_assessment(self, candidate_email, candidate_name, position_name):
        """Send an assessment to a candidate (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_assessment_results(self, assessment_id):
        """Get the results of an assessment (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")

class HackerRankIntegration(LMSIntegration):
    """Integration with HackerRank API"""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def send_assessment(self, candidate_email, candidate_name, position_name):
        """Send a HackerRank test to a candidate"""
        try:
            # Find test ID based on position name (example - would need to be customized)
            test_id = self._get_test_id_for_position(position_name)
            
            # Prepare API payload
            payload = {
                "test_id": test_id,
                "candidates": [
                    {
                        "email": candidate_email,
                        "first_name": candidate_name.split()[0],
                        "last_name": candidate_name.split()[-1] if len(candidate_name.split()) > 1 else ""
                    }
                ],
                "subject": f"Assessment for {position_name} position",
                "message": f"Dear {candidate_name.split()[0]},\n\nPlease complete the following assessment for the {position_name} position."
            }
            
            # Make API request to send test invitation
            response = requests.post(
                f"{self.api_url}/tests/{test_id}/candidates/invite",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Assessment sent to {candidate_email} via HackerRank")
            return {
                "success": True,
                "assessment_id": result.get("assessment_id"),
                "invitation_id": result.get("invitation_id"),
                "status": "sent"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending HackerRank assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_assessment_results(self, assessment_id):
        """Get the results of a HackerRank assessment"""
        try:
            response = requests.get(
                f"{self.api_url}/assessments/{assessment_id}",
                headers=self.headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "status": result.get("status"),
                "score": result.get("score"),
                "completed_at": result.get("completed_at"),
                "results": result.get("results")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting HackerRank assessment results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_test_id_for_position(self, position_name):
        """
        Map position name to test ID
        This is a simplified example - in practice, you would have a mapping or search functionality
        """
        # Example mapping - would need to be customized
        position_to_test_map = {
            "Software Engineer": "12345",
            "Data Scientist": "23456",
            "DevOps Engineer": "34567",
            # Add more mappings as needed
        }
        
        # Default to a general assessment if position not found
        return position_to_test_map.get(position_name, "default_test_id")

class TestGorillaIntegration(LMSIntegration):
    """Integration with TestGorilla API"""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}"
        }
    
    def send_assessment(self, candidate_email, candidate_name, position_name):
        """Send a TestGorilla assessment to a candidate"""
        try:
            # Find assessment ID based on position name
            assessment_id = self._get_assessment_id_for_position(position_name)
            
            # Prepare API payload
            payload = {
                "email": candidate_email,
                "first_name": candidate_name.split()[0],
                "last_name": candidate_name.split()[-1] if len(candidate_name.split()) > 1 else "",
                "language": "en",
                "assessment": assessment_id
            }
            
            # Make API request to send invitation
            response = requests.post(
                f"{self.api_url}/candidates/",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Assessment sent to {candidate_email} via TestGorilla")
            return {
                "success": True,
                "candidate_id": result.get("id"),
                "invitation_url": result.get("invitation_url"),
                "status": "invited"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending TestGorilla assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_assessment_results(self, candidate_id):
        """Get the results of a TestGorilla assessment"""
        try:
            response = requests.get(
                f"{self.api_url}/candidates/{candidate_id}/",
                headers=self.headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "status": result.get("status"),
                "score": result.get("score"),
                "completed_at": result.get("completed_at"),
                "test_results": result.get("test_results", [])
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting TestGorilla assessment results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_assessment_id_for_position(self, position_name):
        """
        Map position name to assessment ID
        This is a simplified example - in practice, you would have a mapping or search functionality
        """
        # Example mapping - would need to be customized
        position_to_assessment_map = {
            "Software Engineer": "abc123",
            "Data Scientist": "def456",
            "DevOps Engineer": "ghi789",
            # Add more mappings as needed
        }
        
        # Default to a general assessment if position not found
        return position_to_assessment_map.get(position_name, "default_assessment_id")

def get_lms_client() -> LMSIntegration:
    """Factory function to get the appropriate LMS client based on configuration"""
    lms_type = settings.LMS_TYPE.lower()
    
    if lms_type == "hackerrank":
        return HackerRankIntegration()
    elif lms_type == "testgorilla":
        return TestGorillaIntegration()
    else:
        logger.warning(f"Unsupported LMS type: {lms_type}, falling back to HackerRank")
        return HackerRankIntegration()
