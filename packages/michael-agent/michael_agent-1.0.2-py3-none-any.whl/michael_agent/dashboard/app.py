"""
Flask dashboard for monitoring the SmartRecruitAgent workflow
"""

import os
from os.path import join
import json
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import logging
import random  # Make sure this is here at the top level
import traceback

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartrecruit2025'

# Initialize Socket.IO for real-time updates
# Configure for async mode with eventlet for production use
try:
    import eventlet
    async_mode = 'eventlet'
    logger.info("Using eventlet for Socket.IO")
except ImportError:
    try:
        import gevent
        async_mode = 'gevent'
        logger.info("Using gevent for Socket.IO")
    except ImportError:
        async_mode = 'threading'
        logger.warning("Using threading mode for Socket.IO - this is not recommended for production use")

socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

# In-memory store for workflow status (in production, use a database)
workflow_logs = []
node_statuses = {
    'jd_generator': {'status': 'idle', 'last_run': None},
    'jd_poster': {'status': 'idle', 'last_run': None},
    'resume_ingestor': {'status': 'idle', 'last_run': None},
    'resume_analyzer': {'status': 'idle', 'last_run': None},
    'sentiment_analysis': {'status': 'idle', 'last_run': None},
    'assessment_handler': {'status': 'idle', 'last_run': None},
    'question_generator': {'status': 'idle', 'last_run': None},
    'recruiter_notifier': {'status': 'idle', 'last_run': None}
}

# Check if a JSON log file exists and load it
LOG_FILE = os.path.join(settings.LOG_DIR, 'workflow_logs.json')
if os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, 'r') as f:
            workflow_logs = json.load(f)
    except Exception as e:
        logger.error(f"Error loading log file: {e}")

# Setup thread variable at module level
background_thread = None

@app.route('/')
def index():
    """Main dashboard route"""
    global background_thread
    
    # Start background thread if it's not already running
    if background_thread is None or not background_thread.is_alive():
        background_thread = threading.Thread(target=background_updater)
        background_thread.daemon = True
        background_thread.start()
        
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/jd-creation')
def jd_creation():
    """Job Description creation page"""
    return render_template('jd_creation.html')

@app.route('/career-portal')
def career_portal():
    """Career portal page for job listings and applications"""
    return render_template('career_portal.html')

@app.route('/resume-scoring')
def resume_scoring():
    """Resume scoring analysis page"""
    return render_template('resume_scoring.html')

@app.route('/upload-resume')
def upload_resume():
    """Resume upload page"""
    return render_template('upload_resume.html')

@app.route('/api/logs')
def get_logs():
    """API endpoint to get workflow logs"""
    return jsonify({
        'logs': workflow_logs,
        'node_statuses': node_statuses
    })

@app.route('/api/status')
def get_status():
    """API endpoint to get current system status"""
    return jsonify({
        'node_statuses': node_statuses,
        'stats': {
            'total_resumes_processed': len(workflow_logs),
            'resumes_today': len([log for log in workflow_logs if 
                                log.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
        }
    })

@app.route('/api/retry', methods=['POST'])
def retry_job():
    """API endpoint to retry a failed job"""
    data = request.json
    job_id = data.get('job_id')
    
    # In a real implementation, this would trigger the LangGraph workflow to retry
    # For now, just update the status in the logs
    for log in workflow_logs:
        if log.get('job_id') == job_id:
            log['status'] = 'retrying'
            
    # Emit update to clients
    socketio.emit('log_update', {'logs': workflow_logs})
    
    return jsonify({'success': True})

def update_node_status(node_name, status, details=None):
    """Update the status of a workflow node"""
    if node_name in node_statuses:
        node_statuses[node_name]['status'] = status
        node_statuses[node_name]['last_run'] = datetime.now().isoformat()
        if details:
            node_statuses[node_name]['details'] = details
            
        # Emit update to clients
        socketio.emit('status_update', {'node_statuses': node_statuses})
        
        # Save to disk
        save_logs_to_file()
    else:
        logger.error(f"Unknown node name: {node_name}")

def add_log_entry(log_data):
    """Add a new log entry to the workflow logs"""
    if 'timestamp' not in log_data:
        log_data['timestamp'] = datetime.now().isoformat()
    
    workflow_logs.append(log_data)
    
    # Emit update to clients
    socketio.emit('log_update', {'logs': workflow_logs})
    
    # Save to disk
    save_logs_to_file()

def save_logs_to_file():
    """Save logs to disk"""
    try:
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        with open(LOG_FILE, 'w') as f:
            json.dump(workflow_logs, f, indent=2, default=str)
            
        # Also write node statuses to separate file
        node_status_file = os.path.join(settings.LOG_DIR, 'node_statuses.json')
        with open(node_status_file, 'w') as f:
            json.dump(node_statuses, f, indent=2, default=str)
            
        logger.debug(f"Log files saved successfully")
    except Exception as e:
        logger.error(f"Error saving log file: {str(e)}")
        logger.error(traceback.format_exc())

# Background thread for dashboard updates
def background_updater():
    """Background thread for periodic dashboard updates"""
    try:
        logger.info("Background updater thread started")
        while True:
            try:
                # Emit heartbeat for client connectivity check
                current_time = datetime.now().isoformat()
                socketio.emit('heartbeat', {'time': current_time})
                
                # Check for any file system changes if needed
                check_for_workflow_updates()
                
                # Sleep for the configured interval
                time.sleep(settings.DASHBOARD_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error in background updater: {str(e)}")
                # Sleep a bit to avoid thrashing in case of persistent errors
                time.sleep(max(5, settings.DASHBOARD_UPDATE_INTERVAL))
    except Exception as e:
        logger.error(f"Fatal error in background updater: {str(e)}")
        logger.error(traceback.format_exc())

def check_for_workflow_updates():
    """Check for updates to workflow status from filesystem"""
    # This function can be expanded to check for new log files, etc.
    pass

with app.app_context():
    def start_background_thread():
        """Start the background thread before the first request"""
        thread = threading.Thread(target=background_updater)
        thread.daemon = True
        thread.start()
    
    # Start the thread immediately
    start_background_thread()

# API for LangGraph nodes to post updates
@app.route('/api/update', methods=['POST'])
def update_workflow():
    """API endpoint for LangGraph nodes to post updates"""
    data = request.json
    
    if 'node_name' in data and 'status' in data:
        update_node_status(data['node_name'], data['status'], data.get('details'))
    
    if 'log_entry' in data:
        add_log_entry(data['log_entry'])
    
    return jsonify({'success': True})

# API endpoints for Job Description creation
@app.route('/api/generate-jd', methods=['POST'])
def generate_jd():
    """API endpoint to generate a job description"""
    data = request.json
    
    try:
        # In a real implementation, this would use the JD generator from LangGraph
        # For demo purposes, we'll simulate a response
        
        from sys import path
        from os.path import dirname, abspath, join
        import importlib.util
        
        # Import the JD generator module
        jd_generator_path = join(dirname(dirname(abspath(__file__))), 
                                'langgraph_workflow', 'nodes', 'jd_generator.py')
        spec = importlib.util.spec_from_file_location("jd_generator", jd_generator_path)
        jd_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(jd_generator)
        
        # Create initial state with job data
        state = {
            "job_description": data,
            "errors": []
        }
        
        # Use the JD generator node to create the job description
        result_state = jd_generator.generate_job_description(state)
        
        return jsonify({
            'success': True,
            'job_description_text': result_state.get('job_description_text', 'Error generating job description')
        })
    except Exception as e:
        logger.error(f"Error generating job description: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-jd', methods=['POST'])
def save_jd():
    try:
        data = request.json
        
        # Create a timestamp-based job ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        job_id = timestamp
        
        # Job data structure
        jd_data = {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "job_data": data.get("metadata", {}),
            "job_description": data.get("content", "")
        }
        
        # Save to job_descriptions directory
        os.makedirs("job_descriptions", exist_ok=True)
        filepath = os.path.join("job_descriptions", f"{job_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(jd_data, f, indent=2)
        
        return jsonify({"success": True, "job_id": job_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# API endpoints for Resume Scoring and Candidate Management
@app.route('/api/jobs')
def get_jobs():
    """API endpoint to get list of jobs"""
    try:
        # In a real implementation, this would fetch from a database
        # For demo purposes, we'll read from saved JSON files
        
        import json
        import os
        import re
        from glob import glob
        from os.path import join
        
        jd_dir = join(settings.JOB_DESCRIPTIONS_DIR)
        if not os.path.exists(jd_dir):
            return jsonify({'jobs': []})
        
        jobs = []
        for jd_file in glob(join(jd_dir, '*.json')):
            try:
                with open(jd_file, 'r') as f:
                    jd_data = json.load(f)
                
                # Extract title from job description using regex
                title_match = re.search(r'\*\*Job Title:\s*(.*?)\*\*', jd_data.get('job_description', ''))
                title = title_match.group(1) if title_match else "Untitled Job"
                
                # Get job ID from filename or job_id field
                job_id = jd_data.get('job_id', os.path.basename(jd_file).split('.')[0])
                
                # Create timestamp if not available
                created_at = jd_data.get('timestamp', jd_data.get('created_at', ''))
                
                jobs.append({
                    'id': job_id,
                    'title': title,
                    'created_at': created_at
                })
            except Exception as e:
                logger.error(f"Error processing job file {jd_file}: {str(e)}")
        
        # Sort by created_at (newest first) with improved safety checks for None values
        def sort_key(x):
            created_at = x.get('created_at')
            # Return a default datetime string for None values to avoid comparison issues
            return created_at if created_at is not None else '1970-01-01T00:00:00'
            
        # Try to sort, but if that fails, return unsorted list rather than failing
        try:
            jobs.sort(key=sort_key, reverse=True)
        except Exception as sort_error:
            logger.warning(f"Error sorting jobs: {str(sort_error)}. Returning unsorted list.")
        
        return jsonify({'jobs': jobs})
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({'jobs': [], 'error': str(e)}), 500

@app.route('/api/career-jobs')
def get_career_jobs():
    """API endpoint to get list of jobs for the career portal"""
    try:
        # In a real implementation, this would fetch from a database
        # For demo purposes, we'll read from saved JSON files
        
        import json
        import os
        from glob import glob
        from os.path import join
        import re
        
        jd_dir = join(settings.JOB_DESCRIPTIONS_DIR)
        logger.info(f"Looking for job descriptions in: {jd_dir}")
        
        if not os.path.exists(jd_dir):
            logger.warning(f"Job descriptions directory does not exist: {jd_dir}")
            return jsonify({'jobs': []})
        
        job_files = glob(join(jd_dir, '*.json'))
        logger.info(f"Found {len(job_files)} job description files")
        
        jobs = []
        for jd_file in job_files:
            try:
                logger.info(f"Processing job file: {jd_file}")
                with open(jd_file, 'r') as f:
                    jd_data = json.load(f)
                
                # Extract title from job description using regex
                title_match = re.search(r'\*\*Job Title:\s*(.*?)\*\*', jd_data.get('job_description', ''))
                title = title_match.group(1) if title_match else "Untitled Job"
                
                # Extract location from job data or job description
                location = "Not specified"
                if 'job_data' in jd_data and 'location' in jd_data['job_data']:
                    location = jd_data['job_data']['location']
                else:
                    location_match = re.search(r'\*\*Location:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
                    if location_match:
                        location = location_match.group(1)
                
                # Extract employment type
                employment_type = "Full-time"
                emp_type_match = re.search(r'\*\*Employment Type:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
                if emp_type_match:
                    employment_type = emp_type_match.group(1)
                
                # Extract experience level
                experience_level = "Not specified"
                exp_level_match = re.search(r'\*\*Experience Level:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
                if exp_level_match:
                    experience_level = exp_level_match.group(1)
                
                # Extract skills from job data
                required_skills = []
                preferred_skills = []
                
                if 'job_data' in jd_data:
                    required_skills = jd_data['job_data'].get('required_skills', [])
                    preferred_skills = jd_data['job_data'].get('preferred_skills', [])
                
                # Get job ID from filename or job_id field
                job_id = jd_data.get('job_id', os.path.basename(jd_file).split('.')[0])
                
                # Create timestamp if not available
                created_at = jd_data.get('timestamp', jd_data.get('created_at', ''))
                
                logger.info(f"Extracted job data: id={job_id}, title={title}, location={location}")
                
                jobs.append({
                    'id': job_id,
                    'title': title,
                    'content': jd_data.get('job_description', ''),
                    'created_at': created_at,
                    'location': location,
                    'employment_type': employment_type,
                    'experience_level': experience_level,
                    'required_skills': required_skills,
                    'preferred_skills': preferred_skills
                })
            except Exception as file_error:
                logger.error(f"Error processing job file {jd_file}: {str(file_error)}")
        
        # Sort by created_at (newest first) with improved safety checks for None values
        def sort_key(x):
            created_at = x.get('created_at')
            # Return a default datetime string for None values to avoid comparison issues
            return created_at if created_at is not None else '1970-01-01T00:00:00'
            
        # Try to sort, but if that fails, return unsorted list rather than failing
        try:
            jobs.sort(key=sort_key, reverse=True)
        except Exception as sort_error:
            logger.warning(f"Error sorting jobs: {str(sort_error)}. Returning unsorted list.")
        
        return jsonify({'jobs': jobs})
    except Exception as e:
        logger.error(f"Error getting jobs for career portal: {str(e)}")
        return jsonify({'jobs': [], 'error': str(e)}), 500

@app.route('/api/jobs/<job_id>')
def get_job(job_id):
    """API endpoint to get job details"""
    try:
        # In a real implementation, this would fetch from a database
        # For demo purposes, we'll read from saved JSON file
        
        import json
        import os
        import re
        
        jd_file = join(settings.JOB_DESCRIPTIONS_DIR, f'{job_id}.json')
        if not os.path.exists(jd_file):
            return jsonify({'error': 'Job not found'}), 404
        
        with open(jd_file, 'r') as f:
            jd_data = json.load(f)
        
        # Extract title from job description using regex
        title_match = re.search(r'\*\*Job Title:\s*(.*?)\*\*', jd_data.get('job_description', ''))
        title = title_match.group(1) if title_match else "Untitled Job"
        
        # Extract location from job data or job description
        location = "Not specified"
        if 'job_data' in jd_data and 'location' in jd_data['job_data']:
            location = jd_data['job_data']['location']
        else:
            location_match = re.search(r'\*\*Location:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
            if location_match:
                location = location_match.group(1)
        
        # Extract employment type
        employment_type = "Full-time"
        emp_type_match = re.search(r'\*\*Employment Type:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
        if emp_type_match:
            employment_type = emp_type_match.group(1)
        
        # Extract experience level
        experience_level = "Not specified"
        exp_level_match = re.search(r'\*\*Experience Level:\*\*\s*(.*?)(?:\n|$)', jd_data.get('job_description', ''))
        if exp_level_match:
            experience_level = exp_level_match.group(1)
        
        # Extract skills from job data
        required_skills = []
        preferred_skills = []
        
        if 'job_data' in jd_data:
            required_skills = jd_data['job_data'].get('required_skills', [])
            preferred_skills = jd_data['job_data'].get('preferred_skills', [])
        
        return jsonify({
            'id': job_id,
            'title': title,
            'content': jd_data.get('job_description', ''),
            'created_at': jd_data.get('timestamp', jd_data.get('created_at', '')),
            'location': location,
            'employment_type': employment_type,
            'experience_level': experience_level,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills
        })
    except Exception as e:
        logger.error(f"Error getting job details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidates')
def get_candidates():
    """API endpoint to get candidates for a job"""
    logger.info(f"Request arguments: {request.args}")
    job_id = request.args.get('job_id')
    logger.info(f"Processing candidates request for job_id: {job_id}")
    
    # Debug logging for settings
    logger.info(f"RESUME_WATCH_DIR setting: {settings.RESUME_WATCH_DIR}")
    logger.info(f"LOG_DIR setting: {settings.LOG_DIR}")
    
    # Import needed modules at the top of the function
    from datetime import datetime, timedelta
    import traceback
    
    # If no job ID is specified, return an error
    if not job_id:
        return jsonify({'error': 'Job ID is required'}), 400
    
    # Filter parameters
    min_score = request.args.get('min_score', type=int, default=0)
    status_filter = request.args.get('status', '').split(',') if request.args.get('status') else []
    logger.info(f"Filters - min_score: {min_score}, status_filter: {status_filter}")
    
    try:
        # Get job details
        import json
        import os
        
        jd_file = join(settings.JOB_DESCRIPTIONS_DIR, f'{job_id}.json')
        if not os.path.exists(jd_file):
            return jsonify({'error': 'Job not found'}), 404
        
        with open(jd_file, 'r') as f:
            jd_data = json.load(f)
        
        metadata = jd_data.get('job_data', {})
        required_skills = metadata.get('required_skills', [])
        
        # Data collections for results and stats
        candidates = []
        score_ranges = {'0-50': 0, '50-70': 0, '70-85': 0, '85-100': 0}
        qualified = 0
        unqualified = 0
        
        # Track processed candidates by email to avoid duplicates
        # We'll prefer data from snapshot files over application metadata
        processed_candidate_emails = {}
        application_candidates = {}
        
        # Define search paths
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(current_dir)
        
        # Look for snapshot files first (these contain the most complete data)
        snapshot_locations = [
            os.path.join(current_dir, 'logs', 'snapshots'),
            os.path.join(project_root, 'logs', 'snapshots'),
            os.path.join(settings.LOG_DIR, 'snapshots'),
            './logs/snapshots'
        ]
        
        # Process snapshot files first (from resume analyzer and question generator)
        snapshot_files = []
        for snapshots_dir in snapshot_locations:
            if os.path.exists(snapshots_dir):
                logger.info(f"Snapshots directory exists at {snapshots_dir}, checking for processed resume files")
                for filename in os.listdir(snapshots_dir):
                    if filename.endswith('.json') and ('after_question_generator' in filename):
                        if job_id in filename:
                            snapshot_path = os.path.join(snapshots_dir, filename)
                            logger.info(f"Adding snapshot file: {snapshot_path}")
                            snapshot_files.append(snapshot_path)
        
        # Process all snapshot files
        for snapshot_file in snapshot_files:
            try:
                with open(snapshot_file, 'r') as f:
                    data = json.load(f)
                
                if data.get('job_id') != job_id:
                    continue
                
                # Extract candidate data from snapshot
                candidate_name = data.get('candidate_name')
                candidate_email = data.get('candidate_email')
                resume_path = data.get('resume_path')
                score = int(float(data.get('relevance_score', 0)) * 100)
                
                # If we have resume_data, use that
                if 'resume_data' in data:
                    resume_data = data['resume_data']
                    if not candidate_name:
                        candidate_name = resume_data.get('name', '')
                    if not candidate_email:
                        candidate_email = resume_data.get('email', '')
                    
                    skills = resume_data.get('skills', [])
                    experience = resume_data.get('experience', [])
                    education = resume_data.get('education', [])
                else:
                    skills = []
                    experience = []
                    education = []
                
                # Skip if no email found
                if not candidate_email:
                    continue
                
                # Create unique key for this candidate
                candidate_key = candidate_email.lower()
                
                # Calculate skills match
                skills_match = {"matched": 0, "total": len(required_skills)}
                matched_skills = []
                if required_skills and skills:
                    for req_skill in required_skills:
                        found = False
                        for skill in skills:
                            if req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower():
                                found = True
                                break
                        matched_skills.append({"name": req_skill, "found": found})
                        if found:
                            skills_match["matched"] += 1
                
                # Add additional skills not in required
                additional_skills = []
                if skills and required_skills:
                    for skill in skills:
                        is_required = False
                        for req_skill in required_skills:
                            if req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower():
                                is_required = True
                                break
                        if not is_required:
                            additional_skills.append(skill)
                
                # Create candidate data
                candidate_data = {
                    'id': os.path.basename(snapshot_file).split('.')[0],
                    'name': candidate_name,
                    'email': candidate_email,
                    'score': score,
                    'status': data.get('status', 'new'),
                    'resume_path': resume_path,
                    'skills': skills,
                    'experience': experience,
                    'education': education,
                    'skills_match': {
                        'matched': skills_match["matched"],
                        'total': skills_match["total"],
                        'required': matched_skills,
                        'additional': additional_skills,
                        'percentage': int(skills_match["matched"] / skills_match["total"] * 100) if skills_match["total"] > 0 else 0
                    },
                    'date_processed': data.get('timestamp', datetime.now().isoformat()),
                    'source': 'snapshot'
                }
                
                # Add or update the candidate
                processed_candidate_emails[candidate_key] = candidate_data
                
                # Update statistics
                if score < 50:
                    score_ranges['0-50'] += 1
                    unqualified += 1
                elif score < 70:
                    score_ranges['50-70'] += 1
                    unqualified += 1
                elif score < 85:
                    score_ranges['70-85'] += 1
                    qualified += 1
                else:
                    score_ranges['85-100'] += 1
                    qualified += 1
                
            except Exception as e:
                logger.error(f"Error processing snapshot file {snapshot_file}: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Now process application files, but only if we don't have snapshot data for them
        resume_locations = [
            os.path.join(current_dir, 'incoming_resumes'),
            os.path.join(project_root, 'incoming_resumes'),
            settings.RESUME_WATCH_DIR,
            './incoming_resumes'
        ]
        
        for resume_dir in resume_locations:
            if os.path.exists(resume_dir) and os.path.isdir(resume_dir):
                for filename in os.listdir(resume_dir):
                    if filename.endswith('.json') and job_id in filename:
                        try:
                            resume_path = os.path.join(resume_dir, filename)
                            with open(resume_path, 'r') as f:
                                data = json.load(f)
                            
                            if data.get('job_id') != job_id:
                                continue
                            
                            candidate_name = data.get('name', '')
                            candidate_email = data.get('email', '')
                            
                            if not candidate_email:
                                continue
                                
                            candidate_key = candidate_email.lower()
                            
                            # Only use application data if we don't have snapshot data
                            if candidate_key not in processed_candidate_emails:
                                application_candidates[candidate_key] = {
                                    'id': os.path.basename(resume_path).split('.')[0],
                                    'name': candidate_name,
                                    'email': candidate_email,
                                    'score': 0,  # No score for application only data
                                    'status': data.get('status', 'new'),
                                    'resume_path': data.get('resume_path', ''),
                                    'skills': [],
                                    'experience': [],
                                    'education': [],
                                    'skills_match': {
                                        'matched': 0,
                                        'total': len(required_skills),
                                        'required': [],
                                        'additional': [],
                                        'percentage': 0
                                    },
                                    'date_processed': data.get('application_date', datetime.now().isoformat()),
                                    'source': 'application'
                                }
                        except Exception as e:
                            logger.error(f"Error processing application file: {str(e)}")
        
        # First add all snapshot candidates to the final list
        candidates = list(processed_candidate_emails.values())
        
        # Then add application candidates only if they aren't already present
        # Commented out to exclude application data completely
        # candidates.extend(list(application_candidates.values()))
        
        # Sort candidates by score (highest first)
        candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Returning {len(candidates)} candidates")
        
        return jsonify({
            'candidates': candidates,
            'statistics': {
                'total': len(candidates),
                'qualified': qualified,
                'unqualified': unqualified,
                'score_ranges': score_ranges
            }
        })
    except Exception as e:
        logger.error(f"Error getting candidates: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidates/<candidate_id>')
def get_candidate(candidate_id):
    """API endpoint to get candidate details"""
    try:
        # Try to locate this candidate in our resume files
        logger.info(f"Looking for candidate details with ID: {candidate_id}")
        
        # Define possible locations for the candidate file
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(current_dir)
        
        # Define locations to search for candidate data
        search_locations = [
            os.path.join(current_dir, 'logs', 'snapshots'),  # Look in snapshots first for most detailed data
            os.path.join(project_root, 'logs', 'snapshots'),
            os.path.join(settings.LOG_DIR, 'snapshots'),
            './logs/snapshots',
            os.path.join(current_dir, 'incoming_resumes'),
            os.path.join(project_root, 'incoming_resumes'),
            os.path.abspath(settings.RESUME_WATCH_DIR),
            './incoming_resumes'
        ]
        
        # Candidate data we'll populate
        candidate_data = None
        
        # Search all locations for candidate files
        for location in search_locations:
            if not os.path.exists(location) or not os.path.isdir(location):
                continue
                
            # First try exact match with candidate_id
            for filename in os.listdir(location):
                if filename.endswith('.json') and candidate_id in filename:
                    file_path = os.path.join(location, filename)
                    logger.info(f"Found candidate file: {file_path}")
                    
                    try:
                        with open(file_path, 'r') as f:
                            candidate_data = json.load(f)
                            break
                    except Exception as e:
                        logger.error(f"Error reading candidate file: {str(e)}")
                        
            if candidate_data:
                break
                
            # Try finding snapshot files (as backup)
            for filename in os.listdir(location):
                if filename.endswith('.json') and ('after_question_generator' in filename):
                    file_path = os.path.join(location, filename)
                    
                    # Check if this snapshot matches our job ID
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            job_id_match = False
                            
                            # Extract job_id from candidate_id if possible
                            if '_' in candidate_id:
                                job_id_from_candidate = candidate_id.split('_')[0]
                                if data.get('job_id') == job_id_from_candidate:
                                    job_id_match = True
                            
                            # If we found a match or if this is the exact candidate
                            if job_id_match or candidate_id in filename:
                                candidate_data = data
                                logger.info(f"Found candidate data in snapshot: {file_path}")
                                break
                    except Exception as e:
                        logger.error(f"Error reading snapshot file: {str(e)}")
                        
            if candidate_data:
                break
        
        if not candidate_data:
            return jsonify({'error': 'Candidate not found'}), 404
        
        # Extract fields from candidate data
        name = candidate_data.get('candidate_name', candidate_data.get('name', ''))
        email = candidate_data.get('candidate_email', candidate_data.get('email', ''))
        phone = ''
        resume_path = candidate_data.get('resume_path', '')
        
        # Get data from resume_data if available
        if 'resume_data' in candidate_data:
            resume_data = candidate_data['resume_data']
            if not name:
                name = resume_data.get('name', '')
            if not email:
                email = resume_data.get('email', '')
            phone = resume_data.get('phone', '')
            
            # Get skills, experience, and education
            skills = resume_data.get('skills', [])
            experience = resume_data.get('experience', [])
            education = resume_data.get('education', [])
        else:
            # Default empty values if resume_data isn't available
            skills = []
            experience = []
            education = []
        
        # Get relevance score
        score = int(float(candidate_data.get('relevance_score', 0)) * 100)
        
        # Get job ID from candidate data or parse from candidate_id
        job_id = candidate_data.get('job_id', '')
        if not job_id and '_' in candidate_id:
            job_id = candidate_id.split('_')[0]
        
        # Get job details to extract required skills
        required_skills = []
        job_file = os.path.join(settings.JOB_DESCRIPTIONS_DIR, f'{job_id}.json')
        if os.path.exists(job_file):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                    if 'job_data' in job_data:
                        required_skills = job_data['job_data'].get('required_skills', [])
            except Exception as e:
                logger.error(f"Error reading job file: {str(e)}")
        
        # Calculate skills analysis
        skills_analysis = {
            'required': [],
            'additional': []
        }
        
        # Make sure skills is a list
        if not isinstance(skills, list):
            skills = []
            
        # Make sure required_skills is a list
        if not isinstance(required_skills, list):
            required_skills = []
        
        # Analyze required skills
        for req_skill in required_skills:
            found = False
            for skill in skills:
                if isinstance(skill, str) and isinstance(req_skill, str):
                    if req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower():
                        found = True
                        break
            skills_analysis['required'].append({
                'name': req_skill,
                'found': found
            })
        
        # Find additional skills
        for skill in skills:
            if not isinstance(skill, str):
                continue
                
            is_required = False
            for req_skill in required_skills:
                if isinstance(req_skill, str):
                    if req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower():
                        is_required = True
                        break
            if not is_required:
                skills_analysis['additional'].append(skill)
        
        # Get sentiment analysis if available
        ai_analysis = {
            'strengths': [],
            'weaknesses': [],
            'overall': "No detailed analysis available."
        }
        
        # Try to extract sentiment data, which might be in different formats
        if 'sentiment_score' in candidate_data:
            sentiment_data = candidate_data['sentiment_score']
            
            # Ensure sentiment_data is properly formatted to avoid errors
            if isinstance(sentiment_data, dict) and sentiment_data.get('sentiment'):
                # Generate a basic analysis based on sentiment score
                sentiment = sentiment_data.get('sentiment')
                positive_score = sentiment_data.get('positive_score', 0)
                negative_score = sentiment_data.get('negative_score', 0)
                
                if sentiment == 'positive':
                    ai_analysis['overall'] = f"The candidate's resume shows a positive outlook with a score of {int(positive_score*100)}%. This indicates good potential for the role."
                    ai_analysis['strengths'] = ["Communication skills reflected in resume", 
                                              "Relevant experience for the position"]
                elif sentiment == 'neutral':
                    ai_analysis['overall'] = f"The candidate's resume shows a neutral outlook with a balanced sentiment profile. Additional screening recommended."
                elif sentiment == 'negative':
                    ai_analysis['overall'] = f"The candidate's resume shows some concerns with a negative score of {int(negative_score*100)}%. Further evaluation recommended."
                    ai_analysis['weaknesses'] = ["Resume may lack enthusiasm", 
                                               "May need additional screening"]
        
        # Check if there are resume strengths and weaknesses in resume_data
        if 'resume_data' in candidate_data:
            resume_data = candidate_data['resume_data']
            
            # Get skills from resume as strengths if no specific strengths exist
            if not ai_analysis['strengths'] and 'skills' in resume_data and resume_data['skills']:
                relevant_skills = [skill for skill in resume_data['skills'] 
                                 if any(req.lower() in skill.lower() for req in required_skills)] if required_skills else []
                
                if relevant_skills:
                    ai_analysis['strengths'] = [f"Demonstrated expertise in {skill}" for skill in relevant_skills[:3]]
                    ai_analysis['overall'] = "The candidate shows relevant skills and experience for the position."
            
            # Look for areas that could be improved based on missing required skills
            if not ai_analysis['weaknesses'] and required_skills:
                missing_skills = []
                for req_skill in required_skills:
                    if not any(req_skill.lower() in skill.lower() for skill in resume_data.get('skills', [])):
                        missing_skills.append(req_skill)
                
                if missing_skills:
                    ai_analysis['weaknesses'] = [f"No demonstrated experience with {skill}" for skill in missing_skills[:3]]
                    
                    if ai_analysis['overall'] == "No detailed analysis available.":
                        ai_analysis['overall'] = "The candidate is missing some key skills but might be trainable."
        
        # If we have relevant experience, mention it as a strength
        if not ai_analysis['strengths'] and 'experience' in candidate_data.get('resume_data', {}):
            experiences = candidate_data['resume_data']['experience']
            if experiences and len(experiences) > 0:
                ai_analysis['strengths'] = ["Has relevant work experience", 
                                           f"Experience at {experiences[0].get('company', 'previous company')}"]
                
                if ai_analysis['overall'] == "No detailed analysis available.":
                    ai_analysis['overall'] = "The candidate has valuable work experience that may be relevant to the role."
        
        # Add more detailed debug logging
        logger.info(f"Returning candidate data for {candidate_id}, name={name}, has_experience={len(experience)}, has_education={len(education)}")
        
        # Return data with sensible defaults for all fields to prevent frontend errors
        response_data = {
            'id': candidate_id,
            'name': name or 'Unknown Candidate',
            'email': email or 'No email provided',
            'phone': phone or 'No phone provided',
            'score': score or 0,
            'skills_analysis': skills_analysis or {
                'required': [],
                'additional': []
            },
            'experience': experience or [],
            'education': education or [],
            'ai_analysis': ai_analysis or {
                'strengths': [],
                'weaknesses': [],
                'overall': 'No analysis available'
            },
            'resume_path': resume_path or '',
            'status': candidate_data.get('status', 'new') or 'new'
        }
        
        # Log the actual data being sent back
        logger.info(f"Response data structure: {list(response_data.keys())}")
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error getting candidate details: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-questions/<candidate_id>', methods=['GET'])
def generate_questions(candidate_id):
    """API endpoint to generate interview questions for a candidate"""
    try:
        logger.info(f"Looking for interview questions for candidate {candidate_id}")
        
        # Define search directories for snapshots
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(current_dir)
        
        log_locations = [
            os.path.join(current_dir, 'logs', 'snapshots'),
            os.path.join(project_root, 'logs', 'snapshots'),
            os.path.join(settings.LOG_DIR, 'snapshots'),
            './logs/snapshots'
        ]
        
        # Extract job ID from candidate ID if possible
        job_id = None
        if '_' in candidate_id:
            job_id = candidate_id.split('_')[0]
        
        # Look for snapshot files with interview questions
        question_data = None
        
        for location in log_locations:
            if not os.path.exists(location) or not os.path.isdir(location):
                continue
                
            # First, look for files specifically matching this candidate
            for filename in os.listdir(location):
                if filename.endswith('.json') and 'after_question_generator' in filename:
                    file_path = os.path.join(location, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            
                            # Check if this is for the right job or candidate
                            if (job_id and data.get('job_id') == job_id) or candidate_id in filename:
                                # If it has interview questions data
                                if 'interview_questions' in data:
                                    question_data = data
                                    logger.info(f"Found interview questions in snapshot: {file_path}")
                                    break
                    except Exception as e:
                        logger.error(f"Error reading question file: {str(e)}")
                        
            if question_data:
                break
        
        # If we found interview questions, use them
        if question_data and 'interview_questions' in question_data:
            logger.info("Using existing questions from snapshot")
            
            # Return the complete interview_questions structure as it is
            return jsonify({
                'success': True,
                'candidate_id': candidate_id,
                'questions': question_data['interview_questions']
            })
        else:
            # If no questions found
            logger.warning("No interview questions found for candidate %s", candidate_id)
            return jsonify({
                'success': False,
                'error': 'Interview questions not found for this candidate'
            }), 404
            
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidates/<candidate_id>/status', methods=['PUT'])
def update_candidate_status(candidate_id):
    """API endpoint to update candidate status"""
    data = request.json
    
    try:
        # In a real implementation, this would update a database
        # For demo purposes, we'll just return success
        return jsonify({
            'success': True,
            'candidate_id': candidate_id,
            'new_status': data.get('status')
        })
    except Exception as e:
        logger.error(f"Error updating candidate status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export-candidates')
def export_candidates():
    """API endpoint to export candidates to CSV"""
    # In a real implementation, this would generate a CSV file
    # For demo purposes, we'll just return a success message
    return jsonify({
        'success': True,
        'message': 'Export functionality would generate a CSV file in a real implementation'
    })

@app.route('/api/apply', methods=['POST'])
def apply_for_job():
    """API endpoint to handle job applications from the career portal"""
    try:
        # Check if all required fields are present
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume_file']
        job_id = request.form.get('job_id')
        name = request.form.get('name')
        email = request.form.get('email')
        
        if not resume_file or not job_id or not name or not email:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check if directory exists and create if not
        import os
        from datetime import datetime
        
        # Create directory structure if not exists
        incoming_dir = os.path.join(settings.RESUME_WATCH_DIR)
        os.makedirs(incoming_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{job_id}_{request.form.get('name').replace(' ', '_')}.{resume_file.filename.split('.')[-1]}"
        filepath = os.path.join(incoming_dir, filename)
        
        # Save the file
        resume_file.save(filepath)
        logger.info(f"Saved resume file to {filepath}")
        
        # Create metadata file with applicant details
        metadata = {
            'job_id': job_id,
            'name': name,
            'email': email,
            'phone': request.form.get('phone', ''),
            'cover_letter': request.form.get('cover_letter', ''),
            'application_date': datetime.now().isoformat(),
            'status': 'new',
            'resume_path': filepath
        }
        
        metadata_path = f"{filepath}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # In a real implementation, trigger the workflow to process the resume
        from langgraph_workflow.graph_builder import process_new_resume
        
        # Get job description
        job_file = os.path.join(settings.JOB_DESCRIPTIONS_DIR, f'{job_id}.json')
        job_description = None
        
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                job_data = json.load(f)
                
                # Extract title from job description using regex
                import re
                title_match = re.search(r'\*\*Job Title:\s*(.*?)\*\*', job_data.get('job_description', ''))
                title = title_match.group(1) if title_match else "Untitled Job"
                
                job_description = {
                    'id': job_id,
                    'title': title,
                    'content': job_data.get('job_description', ''),
                    'metadata': job_data.get('job_data', {})
                }
        
        # We only need to save the file and metadata - the file system watcher will handle the processing
        # This prevents duplicate workflow execution
        logger.info(f"Resume uploaded through career portal - file system watcher will process it automatically")
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'job_id': job_id,
            'resume_path': filepath
        })
        
    except Exception as e:
        error_msg = f"Error processing application: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': error_msg}), 500

def process_candidate_data(data, job_id=None, min_score=None, status_filter=None):
    """Process candidate data from various sources"""
    # If relevance_score is not in the data, add a default value
    if 'relevance_score' not in data:
        data['relevance_score'] = 0.0  # Default score
        
    # Rest of the function remains the same...

def extract_candidate_info(data, job_id=None):
    """Extract candidate information from file data"""
    candidate = {}
    
    # Try to get candidate name and email
    if 'name' in data:
        logger.info("Found name directly in JSON data, assuming it's applicant metadata")
        candidate['name'] = data.get('name', 'Unknown')
        candidate['email'] = data.get('email', '')
        candidate['status'] = data.get('status', 'new')
        candidate['id'] = f"{job_id}_{data['name'].replace(' ', '_')}"
        candidate['resume_path'] = data.get('resume_path', '')
        
        # Set default relevance score if not available
        candidate['relevance_score'] = 0.0
        
        # Add application date if available
        if 'application_date' in data:
            candidate['application_date'] = data.get('application_date', '')
            
    elif 'resume_data' in data:
        logger.info("Found resume_data key, using that for candidate data")
        candidate['name'] = data.get('candidate_name', 'Unknown')
        candidate['email'] = data.get('candidate_email', '')
        candidate['status'] = data.get('status', 'new')
        candidate['id'] = data.get('timestamp', '').split('_')[0]  # Use timestamp as ID
        candidate['resume_path'] = data.get('resume_path', '')
        
        # Add relevance score if available, otherwise default to 0
        candidate['relevance_score'] = 0.0
        if 'relevance_score' in data:
            candidate['relevance_score'] = data['relevance_score']
            
    elif 'candidate_name' in data:
        logger.info("Found candidate_name key directly in JSON data")
        candidate['name'] = data.get('candidate_name', 'Unknown')
        candidate['email'] = data.get('candidate_email', '')
        candidate['status'] = data.get('status', 'new')
        candidate['id'] = f"{job_id}_{data['candidate_name'].replace(' ', '_')}"
        candidate['resume_path'] = data.get('resume_path', '')
        
        # Add relevance score if available
        candidate['relevance_score'] = 0.0
        if 'relevance_score' in data:
            candidate['relevance_score'] = data['relevance_score']
    
    return candidate

@app.route('/resumes/<candidate_id>')
def serve_resume(candidate_id):
    """Serve the resume PDF file for a candidate"""
    try:
        # Import necessary modules
        import os
        from flask import send_file, abort
        import glob
        
        logger.info(f"Looking for resume file for candidate: {candidate_id}")
        
        # Extract job ID from candidate ID
        job_id = None
        if '_' in candidate_id:
            job_id = candidate_id.split('_')[0]
            logger.info(f"Extracted job ID: {job_id}")
        
        # Define locations to search for resume files
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(current_dir)
        
        search_locations = [
            os.path.join(current_dir, 'incoming_resumes'),
            os.path.join(project_root, 'incoming_resumes'),
            os.path.abspath(settings.RESUME_WATCH_DIR),
            os.path.join(current_dir, 'processed_resumes'),
            os.path.join(project_root, 'processed_resumes'),
            './incoming_resumes',
            './processed_resumes'
        ]
        
        # Search for resume path in snapshot files first
        snapshot_locations = [
            os.path.join(current_dir, 'logs', 'snapshots'),
            os.path.join(project_root, 'logs', 'snapshots'),
            os.path.join(settings.LOG_DIR, 'snapshots'),
            './logs/snapshots'
        ]
        
        # First check for resume path in snapshot files
        resume_path = None
        for snapshot_dir in snapshot_locations:
            if not os.path.exists(snapshot_dir) or not os.path.isdir(snapshot_dir):
                continue
                
            # Look for snapshot files for this candidate/job
            for filename in os.listdir(snapshot_dir):
                if filename.endswith('.json') and ('after_question_generator' in filename):
                    # Check if this snapshot file is for our candidate
                    if job_id and job_id in filename:
                        snapshot_path = os.path.join(snapshot_dir, filename)
                        logger.info(f"Checking snapshot file: {snapshot_path}")
                        
                        try:
                            with open(snapshot_path, 'r') as f:
                                data = json.load(f)
                                if 'resume_path' in data:
                                    resume_path = data['resume_path']
                                    logger.info(f"Found resume path in snapshot: {resume_path}")
                                    break
                        except Exception as e:
                            logger.error(f"Error reading snapshot file: {str(e)}")
            
            if resume_path:
                break
        
        # If we found a resume path in the snapshot, check if it exists
        if resume_path:
            # Handle relative paths
            if resume_path.startswith('./'):
                absolute_paths_to_try = [
                    os.path.join(current_dir, resume_path[2:]),
                    os.path.join(project_root, resume_path[2:]),
                    os.path.abspath(resume_path),
                    resume_path
                ]
                
                for path in absolute_paths_to_try:
                    if os.path.exists(path):
                        logger.info(f"Found resume at absolute path: {path}")
                        return send_file(path, mimetype='application/pdf')
        
        # If no resume found from snapshot path, search directly for PDF files
        for location in search_locations:
            if not os.path.exists(location) or not os.path.isdir(location):
                continue
                
            logger.info(f"Searching directory: {location}")
            # First try exact match
            for filename in os.listdir(location):
                logger.info(f"Found file: {filename}")
                if filename.endswith('.pdf') and candidate_id in filename:
                    pdf_path = os.path.join(location, filename)
                    logger.info(f"Found exact match resume: {pdf_path}")
                    return send_file(pdf_path, mimetype='application/pdf')
            
            # If no exact match, try job ID match
            if job_id:
                for filename in os.listdir(location):
                    if filename.endswith('.pdf') and job_id in filename:
                        pdf_path = os.path.join(location, filename)
                        logger.info(f"Found resume by job ID: {pdf_path}")
                        return send_file(pdf_path, mimetype='application/pdf')
        
        # As a last resort, try using glob to find files matching the pattern
        if job_id:
            for location in search_locations:
                if not os.path.exists(location):
                    continue
                
                # Look for PDFs containing the job ID
                pattern = os.path.join(location, f"*{job_id}*.pdf")
                logger.info(f"Trying glob pattern: {pattern}")
                matching_files = glob.glob(pattern)
                
                if matching_files:
                    logger.info(f"Found resume via glob: {matching_files[0]}")
                    return send_file(matching_files[0], mimetype='application/pdf')
        
        # If nothing found, log error and return 404
        logger.error(f"Resume not found for candidate {candidate_id}")
        return jsonify({'error': 'Resume file not found'}), 404
        
    except Exception as e:
        logger.error(f"Error serving resume: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Only run directly if this file is executed directly,
    # not when imported as a module
    try:
        import eventlet
        eventlet.monkey_patch()
        logger.info("Eventlet monkey patching applied")
    except ImportError:
        logger.warning("Eventlet not available - WebSocket functionality may be limited")
        
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
