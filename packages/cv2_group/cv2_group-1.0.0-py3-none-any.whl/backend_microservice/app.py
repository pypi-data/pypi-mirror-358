"""
Root Segmentation and Analysis API - Main Application Entry Point

This module serves as the main entry point for the FastAPI application.
All functionality has been modularized into separate packages for better organization.
"""

import logging  # Import logging for logging and logging only

from backend_microservice.app_factory import create_app
from backend_microservice.routes import chat, feedback, health, prediction, upload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = create_app()

# Register all route modules
app.include_router(health.router, tags=["Health & Dashboard"])
app.include_router(feedback.router, tags=["Feedback"])
app.include_router(prediction.router, tags=["Prediction"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(chat.router, tags=["Chat"])


logger.info("Application initialized successfully with all routes registered")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
