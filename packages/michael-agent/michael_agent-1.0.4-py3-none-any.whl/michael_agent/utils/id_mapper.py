import os
import json
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

def get_timestamp_id(job_id: str) -> str:
    """For backward compatibility: return the same job_id"""
    return job_id
    
def get_all_ids_for_timestamp(timestamp_id: str) -> List[str]:
    """For backward compatibility: return list with same job_id"""
    return [timestamp_id]