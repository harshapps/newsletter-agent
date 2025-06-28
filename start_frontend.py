#!/usr/bin/env python3
"""
Startup script for the Newsletter Agent MCP Frontend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit frontend"""
    print("🎨 Starting Newsletter Agent MCP Frontend...")
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Start Streamlit
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main() 