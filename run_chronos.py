#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="CHRONOS AI Launcher")
    parser.add_argument('--mode', choices=['api', 'dashboard', 'both', 'setup'], 
                       default='both', help='Run mode')
    parser.add_argument('--port-api', type=int, default=8000, help='API port')
    parser.add_argument('--port-dashboard', type=int, default=8501, help='Dashboard port')
    parser.add_argument('--dev', action='store_true', help='Development mode')
    
    args = parser.parse_args()
    
    print("🤖 CHRONOS AI - Intelligent Time Orchestrator")
    print("=" * 50)
    
    if args.mode == 'setup':
        run_setup()
        return
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Run with --mode setup first.")
        return
    
    # Run selected mode
    if args.mode == 'api':
        run_api(args.port_api, args.dev)
    elif args.mode == 'dashboard':
        run_dashboard(args.port_dashboard)
    elif args.mode == 'both':
        run_both(args.port_api, args.port_dashboard, args.dev)

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env and configure.")
        return False
    
    required_vars = ['NOTION_TOKEN', 'DATABASE_ID', 'CLAUDE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration OK")
    return True

def run_setup():
    """Run initial setup"""
    print("🔧 Running CHRONOS AI setup...")
    
    # Create .env file if not exists
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Initialize database
    print("🗄️ Initializing database...")
    from core.scheduler import ChronosCore
    try:
        # This will create the database tables
        config = {
            'notion_token': 'dummy',
            'database_id': 'dummy',
            'claude_api_key': 'dummy'
        }
        chronos = ChronosCore(config)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    print("🎉 Setup complete! Please configure your .env file and run again.")

def run_api(port, dev_mode):
    """Run API server"""
    print(f"🚀 Starting CHRONOS AI API on port {port}")
    
    cmd = [
        'uvicorn', 'api.main:app',
        '--host', '0.0.0.0',
        '--port', str(port)
    ]
    
    if dev_mode:
        cmd.append('--reload')
    
    subprocess.run(cmd)

def run_dashboard(port):
    """Run dashboard"""
    print(f"📊 Starting CHRONOS AI Dashboard on port {port}")
    
    subprocess.run([
        'streamlit', 'run', 'dashboard/app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0'
    ])

def run_both(api_port, dashboard_port, dev_mode):
    """Run both API and dashboard"""
    import threading
    import time
    
    print(f"🚀 Starting CHRONOS AI (API: {api_port}, Dashboard: {dashboard_port})")
    
    # Start API in background thread
    def start_api():
        run_api(api_port, dev_mode)
    
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Wait a bit for API to start
    time.sleep(3)
    
    # Start dashboard (blocking)
    run_dashboard(dashboard_port)

if __name__ == '__main__':
    main()