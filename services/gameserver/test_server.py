"""
Simple FastAPI test server to verify port binding in Replit
"""
from fastapi import FastAPI
import uvicorn
import os
import sys

# Show environment information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")
print(f"Environment variables: {dict(os.environ)}")

# Create a minimal FastAPI app
app = FastAPI(
    title="Test API Server",
    description="Simple test to verify port binding",
)

@app.get("/")
async def root():
    return {"message": "Hello World", "status": "OK"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run the server directly
if __name__ == "__main__":
    print("Starting test server on port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)