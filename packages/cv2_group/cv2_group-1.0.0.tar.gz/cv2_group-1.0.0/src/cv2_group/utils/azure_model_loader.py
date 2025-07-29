import logging
import os

import mlflow
from azure.ai.ml import MLClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from cv2_group.utils.helpers import f1, precision, recall

# --- Required Environment Variables ---
#   AZURE_SUBSCRIPTION_ID
#   AZURE_RESOURCE_GROUP
#   AZURE_WORKSPACE_NAME
#   AZURE_TENANT_ID
#   AZURE_CLIENT_ID
#   AZURE_CLIENT_SECRET
#   AZURE_MODEL_NAME
#   AZURE_MODEL_LABEL (optional, defaults to 'latest')

# F821 undefined name 'CUSTOM_OBJECTS' - This variable is defined here,
# but if it was truly undefined in the context where flake8 reported it
# (likely another file that *uses* model_evaluation.py), then that file
# would need to import CUSTOM_OBJECTS from here.
# For this file, it is correctly defined.
CUSTOM_OBJECTS = {"f1": f1, "precision": precision, "recall": recall}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


def load_model_from_azure_registry(model_name=None, model_label=None):
    """
    Load a trained model from the Azure ML Model Registry.

    This function retrieves a registered model using Azure ML SDK, downloading
    its artifacts locally, then attempts to load the model using MLflow's Keras
    flavor or falls back to the generic PyFunc flavor.

    Configuration parameters such as model name, model label, Azure subscription,
    resource group, workspace name, and credentials are read from environment
    variables if not provided as arguments.

    Parameters
    ----------
    model_name : str, optional
        Name of the model to load. If None, reads from 'AZURE_MODEL_NAME' env var.
    model_label : str, optional
        Label/version of the model to load (e.g., 'latest'). Defaults to 'latest'.

    Raises
    ------
    EnvironmentError
        If required Azure environment variables are missing.
    FileNotFoundError
        If downloaded model artifacts are not found in expected paths.
    Exception
        If loading the model fails at any stage.

    Returns
    -------
    The loaded model object (Keras model or MLflow PyFunc model).
    """
    model_name = model_name or os.environ.get("AZURE_MODEL_NAME")
    model_label = model_label or os.environ.get("AZURE_MODEL_LABEL", "latest")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    resource_group = os.environ.get("AZURE_RESOURCE_GROUP")
    workspace_name = os.environ.get("AZURE_WORKSPACE_NAME")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")

    if not all(
        [
            model_name,
            subscription_id,
            resource_group,
            workspace_name,
            tenant_id,
            client_id,
            client_secret,
        ]
    ):
        raise EnvironmentError(
            "Missing one or more required Azure environment variables."
        )

    logger.info(
        f"Retrieving model '{model_name}' with label '{model_label}' "
        "from Azure ML..."
    )

    # Credential Setup
    try:
        credential = DefaultAzureCredential()
        # E501: Breaking long line
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # E501: Breaking long f-string
        logger.warning(
            f"DefaultAzureCredential failed: {ex}. Falling back to "
            "ClientSecretCredential."
        )
        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )

    # E501: Breaking long constructor call
    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )
    logger.info("✅ Authenticated with Azure ML.")

    try:
        model = ml_client.models.get(name=model_name, label=model_label)
        # E501: Breaking long f-string
        logger.info(
            f"Model found: {model.name} (version {model.version}, "
            f"label {model_label})."
        )
        # E501: Breaking long os.path.join call
        download_dir = os.path.join(
            "downloaded_registered_models", model.name, model.version
        )
        os.makedirs(download_dir, exist_ok=True)
        # E501: Breaking long method call
        ml_client.models.download(
            name=model.name, version=model.version, download_path=download_dir
        )
        logger.info(f"Downloaded model to: {download_dir}")
        # E501: Breaking long os.path.join call
        mlflow_path = os.path.join(
            download_dir, model.name, "temp_mlflow_model_for_registration"
        )
        if not os.path.exists(mlflow_path):
            mlflow_path = os.path.join(download_dir, model.name)
            if not os.path.exists(mlflow_path):
                mlflow_path = download_dir
        if not os.path.exists(mlflow_path):
            # E501: Breaking long f-string
            logger.error(
                f"❌ MLflow path not found: {mlflow_path}. Check the artifact "
                "structure."
            )
            # E501: Breaking long f-string
            raise FileNotFoundError(f"Missing MLflow model artifacts at: {mlflow_path}")
        logger.info(f"Loading model from: {mlflow_path}")
        # Try to load as a Keras model using MLflow's keras flavor
        try:
            keras_model = mlflow.keras.load_model(mlflow_path)
            # E501: Breaking long string
            logger.info("✅ Loaded Keras model using mlflow.keras.load_model.")
            return keras_model
        except Exception as e:
            # E501: Breaking long f-string
            logger.warning(f"mlflow.keras.load_model failed: {e}")
        # Fallback: try loading as a generic MLflow PyFunc model
        try:
            pyfunc_model = mlflow.pyfunc.load_model(mlflow_path)
            # E501: Breaking long string
            logger.info("✅ Loaded MLflow PyFunc model.")
            return pyfunc_model
        except Exception as e:
            # E501: Breaking long f-string
            logger.error(f"Failed to load model from Azure ML: {e}")
            raise
    except Exception as ex:
        # E501: Breaking long f-string
        logger.error(f"Failed to load model from Azure ML: {ex}")
        raise
