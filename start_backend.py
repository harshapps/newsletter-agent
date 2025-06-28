#!/usr/bin/env python3
"""
Startup script for the Newsletter Agent MCP Backend
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Start the FastAPI backend server"""
    print("🚀 Starting Newsletter Agent MCP Backend...")
    
    # Check if required environment variables are set
    required_vars = ["OPENAI_API_KEY", "MONGODB_URI"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before starting the server.")
        print("You can create a .env file in the project root with:")
        for var in missing_vars:
            if var == "OPENAI_API_KEY":
                print(f"   {var}=your_openai_api_key_here")
            elif var == "MONGODB_URI":
                print(f"   {var}=mongodb://localhost:27017/newsletter_agent")
        print()
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 