#!/usr/bin/env python3
"""
SmartRecruitAgent Workflow Monitor CLI
Command-line utility for monitoring workflow progress
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime

# Make sure we can import from our project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our utilities
from utils.monitor_utils import monitor_active_jobs, show_job_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="SmartRecruitAgent Workflow Monitor")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor active jobs")
    monitor_parser.add_argument(
        "--refresh", "-r", 
        type=int, 
        default=10, 
        help="Refresh interval in seconds (default: 10)"
    )
    
    # Job details command
    details_parser = subparsers.add_parser("details", help="Show details for a specific job")
    details_parser.add_argument(
        "job_id", 
        help="The ID of the job to show details for"
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    if args.command == "monitor":
        try:
            # Show initial state
            os.system('clear' if os.name == 'posix' else 'cls')
            monitor_active_jobs()
            
            # If refresh interval is provided, keep refreshing
            if args.refresh > 0:
                print(f"\nRefreshing every {args.refresh} seconds. Press Ctrl+C to exit.")
                
                while True:
                    time.sleep(args.refresh)
                    os.system('clear' if os.name == 'posix' else 'cls')
                    monitor_active_jobs()
                    print(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Refreshing every {args.refresh} seconds. Press Ctrl+C to exit.")
        except KeyboardInterrupt:
            print("\nExiting monitor.")
    
    elif args.command == "details":
        show_job_details(args.job_id)
    
    else:
        # Default to showing active jobs
        monitor_active_jobs()

if __name__ == "__main__":
    main()
