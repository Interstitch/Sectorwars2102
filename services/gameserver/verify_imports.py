#!/usr/bin/env python3
"""
Simple test script to verify Python module imports in Replit
"""
import os
import sys
import importlib.util

# Print environment information
print(f"Python Version: {sys.version}")
print(f"Python Path: {sys.path}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"PYTHONPATH environment variable: {os.environ.get('PYTHONPATH', 'Not set')}")

# List of modules to check
modules_to_check = [
    "uvicorn", 
    "fastapi",
    "pydantic",
    "starlette",
    "sqlalchemy"
]

# Check each module
print("\nModule Import Check:")
for module_name in modules_to_check:
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ {module_name}: Successfully imported from {module.__file__}")
        else:
            print(f"❌ {module_name}: Module specification not found")
    except ImportError as e:
        print(f"❌ {module_name}: Import error - {str(e)}")
    except Exception as e:
        print(f"❌ {module_name}: Unexpected error - {str(e)}")

# Try to import and run a minimal FastAPI app
print("\nTrying to create a minimal FastAPI app:")
try:
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    
    print("✅ Successfully created a FastAPI app")
    
    # Try to import and initialize uvicorn
    import uvicorn
    print(f"✅ Successfully imported uvicorn from {uvicorn.__file__}")
    
    # Show how we would run this app
    print("The app can be run with: uvicorn.run(app, host='0.0.0.0', port=5000)")
    
except Exception as e:
    print(f"❌ Error creating FastAPI app: {str(e)}")

print("\nVerification complete")