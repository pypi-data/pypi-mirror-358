import logging
import os

# Add these imports for MLClient
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Load environment variables from .env if present
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend_microservice.config import (
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    STATIC_FILES_DIR,
)
from backend_microservice.routes import model_comparison
from cv2_group.utils.azure_integration import initialize_azure_workspace
from cv2_group.utils.dashboard_stats import reset_dashboard_stats
from cv2_group.utils.feedback_system import initialize_feedback_storage

print("AZURE_SUBSCRIPTION_ID:", os.getenv("AZURE_SUBSCRIPTION_ID"))
print("AZURE_RESOURCE_GROUP:", os.getenv("AZURE_RESOURCE_GROUP"))
print("AZURE_WORKSPACE_NAME:", os.getenv("AZURE_WORKSPACE_NAME"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ml_client():
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
    credential = DefaultAzureCredential()
    return MLClient(credential, subscription_id, resource_group, workspace_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Advanced root segmentation and analysis,"
        "API for plant science research",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    initialize_services()
    try:
        app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    app.include_router(model_comparison.router)
    return app


def initialize_services():
    """Initialize all required services"""
    logger.info("Initializing services...")
    azure_success = initialize_azure_workspace()
    if azure_success:
        logger.info("Azure ML workspace initialized successfully")
    else:
        logger.warning(
            "Azure ML workspace initialization failed - ",
            "upload functionality may not work",
        )
    try:
        ml_client = get_ml_client()
        initialize_feedback_storage(ml_client)
        logger.info("Feedback storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize feedback storage: {e}")
    reset_dashboard_stats()
    logger.info("Dashboard statistics reset")
    logger.info("Service initialization complete")
