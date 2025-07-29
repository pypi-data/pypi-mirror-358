import os
from typing import List

# CORS Configuration
CORS_ORIGINS: List[str] = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "null",

    "https://root-backend.icybay-728baac8.westeurope.azurecontainerapps.io",  # Back
    "https://root-frontend.icybay-728baac8.westeurope.azurecontainerapps.io",  # Front

    "http://194.171.191.227:3165",  # Portainer frontend
    "http://194.171.191.227:3166",  # Portainer backend
]

# API Configuration
API_TITLE = "Root Segmentation and Analysis API"
API_VERSION = "1.0.0"

# File Upload Configuration
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
MAX_IMAGES_PER_REQUEST = 16

# Processing Configuration
DEFAULT_TIMEOUT = 300  # 5 minutes
AZURE_MODEL_TIMEOUT = 300  # 5 minutes for Azure model calls

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Static Files Configuration
STATIC_FILES_DIR = "static"
FEEDBACK_IMAGES_DIR = "feedback_images"

# Environment-specific settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
