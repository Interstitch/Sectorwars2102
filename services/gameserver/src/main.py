from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Sector Wars 2102 Game API",
    description="API for the Sector Wars 2102 space trading game",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gameserver"}

# Hello World endpoint
@app.get("/")
async def hello_world():
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Hello from Sector Wars 2102 Game API!",
        "environment": environment,
        "status": "operational"
    }

# API version endpoint
@app.get("/api/version")
async def api_version():
    return {"version": "0.1.0"}

# Start the application
if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment or use 8080 as default for Replit
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)