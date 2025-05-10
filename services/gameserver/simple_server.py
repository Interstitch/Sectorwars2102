#!/usr/bin/env python3
"""
Simple FastAPI test server that doesn't import local modules
- Tests if basic FastAPI and uvicorn work in Replit
- No dependencies on project-specific code
"""
import os
import sys

# Print environment information first
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

try:
    from fastapi import FastAPI
    import uvicorn
    
    # Create a minimal FastAPI application
    app = FastAPI(title="Simple Test Server")
    
    @app.get("/")
    async def root():
        return {
            "message": "Simple test server is running", 
            "python_version": sys.version,
            "environment": os.environ.get("ENVIRONMENT", "Not set")
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    # Direct execution entry point
    if __name__ == "__main__":
        print("Starting simple test server on port 5000...")
        uvicorn.run("simple_server:app", host="0.0.0.0", port=5000)
except Exception as e:
    print(f"ERROR: Failed to import or start server: {e}")
    sys.exit(1)