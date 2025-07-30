"""
Workflow monitoring utility for SmartRecruitAgent
Provides tools to monitor and track workflow progress
"""

import os
import json
import time
import logging
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tabulate import tabulate

# Import config
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_log_entries(log_file_path: str, hours: int = 24) -> List[Dict]:
    """Load log entries from the specified file, filtered by time range"""
    if not os.path.exists(log_file_path):
        logger.warning(f"Log file not found: {log_file_path}")
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    entries = []
    
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                try:
                    # Parse the log line to extract timestamp and JSON content
                    parts = line.strip().split(' | ', 3)
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        log_level = parts[1]
                        module = parts[2]
                        message = parts[3]
                        
                        # Parse timestamp
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        # Skip entries older than cutoff time
                        if timestamp < cutoff_time:
                            continue
                            
                        # For state_transitions.log, message is a JSON string
                        if 'state_transitions' in log_file_path:
                            try:
                                data = json.loads(message)
                                data['timestamp'] = timestamp_str
                                data['log_level'] = log_level
                                entries.append(data)
                            except json.JSONDecodeError:
                                logger.debug(f"Failed to parse JSON: {message}")
                        else:
                            # For regular logs
                            entries.append({
                                'timestamp': timestamp_str,
                                'log_level': log_level,
                                'module': module,
                                'message': message
                            })
                except Exception as e:
                    logger.debug(f"Error parsing log line: {e}")
                    continue
    except Exception as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
    
    return entries

def load_state_snapshots(hours: int = 24) -> Dict[str, Dict]:
    """Load state snapshots from the last specified hours"""
    snapshots_dir = os.path.join(settings.LOG_DIR, "snapshots")
    if not os.path.exists(snapshots_dir):
        logger.warning(f"Snapshots directory not found: {snapshots_dir}")
        return {}
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    snapshots = {}
    
    try:
        for filename in os.listdir(snapshots_dir):
            if not filename.endswith('.json'):
                continue
                
            filepath = os.path.join(snapshots_dir, filename)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Skip files older than cutoff time
            if file_mtime < cutoff_time:
                continue
                
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    snapshots[filename] = data
            except Exception as e:
                logger.debug(f"Error reading snapshot {filename}: {e}")
    except Exception as e:
        logger.error(f"Error accessing snapshots directory: {e}")
    
    return snapshots

def generate_workflow_summary(hours: int = 24) -> pd.DataFrame:
    """Generate a summary of workflow executions from the logs"""
    workflow_logs = load_log_entries(os.path.join(settings.LOG_DIR, 'workflow.log'), hours)
    
    # Extract job IDs and create a summary
    job_data = {}
    for entry in workflow_logs:
        message = entry.get('message', '')
        
        # Try to extract job ID from message
        if '[Job ' in message:
            parts = message.split('[Job ', 1)[1].split(']', 1)
            if len(parts) >= 2:
                job_id = parts[0].strip()
                msg_content = parts[1].strip()
                
                if job_id not in job_data:
                    job_data[job_id] = {
                        'start_time': entry.get('timestamp'),
                        'last_update': entry.get('timestamp'),
                        'steps_completed': 0,
                        'current_status': 'Unknown',
                        'errors': 0
                    }
                
                # Update job data
                job_data[job_id]['last_update'] = entry.get('timestamp')
                
                if 'Step ' in msg_content:
                    job_data[job_id]['steps_completed'] += 1
                
                if 'completed:' in msg_content:
                    status = msg_content.split('completed:', 1)[1].strip()
                    job_data[job_id]['current_status'] = status
                
                if 'Error' in message or 'error' in message:
                    job_data[job_id]['errors'] += 1
    
    # Convert to DataFrame for easier display
    if job_data:
        df = pd.DataFrame.from_dict(job_data, orient='index')
        df.index.name = 'job_id'
        return df
    else:
        return pd.DataFrame(columns=['start_time', 'last_update', 'steps_completed', 'current_status', 'errors'])

def display_errors(hours: int = 24) -> pd.DataFrame:
    """Display all errors from the workflow logs"""
    workflow_logs = load_log_entries(os.path.join(settings.LOG_DIR, 'workflow.log'), hours)
    
    error_entries = []
    for entry in workflow_logs:
        message = entry.get('message', '')
        if entry.get('log_level') == 'ERROR' or 'Error' in message or 'error' in message:
            # Try to extract job ID from message
            job_id = 'Unknown'
            if '[Job ' in message:
                try:
                    job_id = message.split('[Job ', 1)[1].split(']', 1)[0].strip()
                except:
                    pass
                    
            error_entries.append({
                'timestamp': entry.get('timestamp'),
                'job_id': job_id,
                'error': message
            })
    
    # Convert to DataFrame for easier display
    if error_entries:
        df = pd.DataFrame(error_entries)
        return df
    else:
        return pd.DataFrame(columns=['timestamp', 'job_id', 'error'])

def generate_job_timeline(job_id: str) -> Dict:
    """Generate a timeline of steps for a specific job"""
    workflow_logs = load_log_entries(os.path.join(settings.LOG_DIR, 'workflow.log'))
    
    timeline = []
    for entry in workflow_logs:
        message = entry.get('message', '')
        if f'[Job {job_id}]' in message:
            timestamp = entry.get('timestamp')
            
            # Extract step information if available
            if 'Step ' in message and 'completed:' in message:
                try:
                    step_num = int(message.split('Step ', 1)[1].split(' ', 1)[0])
                    step_name = message.split('completed:', 1)[1].strip()
                    
                    timeline.append({
                        'timestamp': timestamp,
                        'step_number': step_num,
                        'step_name': step_name
                    })
                except:
                    pass
    
    return sorted(timeline, key=lambda x: x.get('step_number', 0))

def monitor_active_jobs():
    """Display a summary of active jobs in the terminal"""
    print("\n" + "="*80)
    print(" SmartRecruitAgent Workflow Monitor ".center(80, "="))
    print("="*80)
    
    # Get workflow summary
    df = generate_workflow_summary(hours=24)
    
    if df.empty:
        print("\nNo active jobs found in the last 24 hours.")
    else:
        # Calculate job duration
        df['duration'] = pd.to_datetime(df['last_update']) - pd.to_datetime(df['start_time'])
        df['duration'] = df['duration'].astype(str).str.split('.').str[0]  # Format duration
        
        # Format the output
        summary_df = df[['start_time', 'duration', 'steps_completed', 'current_status', 'errors']].copy()
        print(f"\nActive Jobs (Last 24 Hours): {len(summary_df)}")
        print(tabulate(summary_df, headers='keys', tablefmt='grid'))
    
    # Display recent errors
    error_df = display_errors(hours=6)
    if not error_df.empty:
        print("\nRecent Errors (Last 6 Hours):")
        print(tabulate(error_df, headers='keys', tablefmt='grid', maxcolwidths=[20, 10, 50]))
    
    print("\n" + "="*80)

def show_job_details(job_id: str):
    """Show detailed information for a specific job"""
    timeline = generate_job_timeline(job_id)
    
    print("\n" + "="*80)
    print(f" Job Details: {job_id} ".center(80, "="))
    print("="*80)
    
    if not timeline:
        print(f"\nNo data found for job ID: {job_id}")
        return
        
    # Print timeline
    print("\nExecution Timeline:")
    for step in timeline:
        print(f"[{step['timestamp']}] Step {step['step_number']}: {step['step_name']}")
    
    # Look for snapshots for this job
    snapshots = load_state_snapshots()
    job_snapshots = {k: v for k, v in snapshots.items() if job_id in k}
    
    if job_snapshots:
        print("\nState Snapshots Available:")
        for filename in job_snapshots:
            print(f" - {filename}")
            
        # Print the latest snapshot details
        latest = max(job_snapshots.keys())
        print(f"\nLatest State ({latest}):")
        snapshot = job_snapshots[latest]
        
        # Print key information
        if 'candidate_name' in snapshot:
            print(f"Candidate: {snapshot.get('candidate_name', 'Unknown')}")
        if 'candidate_email' in snapshot:
            print(f"Email: {snapshot.get('candidate_email', 'Unknown')}")
        if 'resume_path' in snapshot:
            print(f"Resume: {snapshot.get('resume_path', 'Unknown')}")
        if 'relevance_score' in snapshot and snapshot['relevance_score'] is not None:
            print(f"Relevance Score: {snapshot.get('relevance_score', 'N/A')}")
        
        # Print any errors
        if 'errors' in snapshot and snapshot['errors']:
            print("\nErrors:")
            for error in snapshot['errors']:
                print(f" - [{error.get('step', 'unknown')}] {error.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    monitor_active_jobs()
