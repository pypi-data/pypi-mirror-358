import logging

from cv2_group.utils.azure_model_loader import load_model_from_azure_registry

logger = logging.getLogger(__name__)


def load_trained_model():
    """
    Always load the 'local' model from the Azure Model
    Registry using environment variables.

    Returns
    -------
    keras.models.Model
        The loaded Keras model from Azure Model Registry.
    """
    logger.info("Loading 'local' model from Azure Model Registry...")
    model = load_model_from_azure_registry()
    logger.info("Model loaded successfully from Azure Model Registry.")
    return model
