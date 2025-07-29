'''
import streamlit as st

from cv2_group.data.data_ingestion import load_image
from cv2_group.data.data_processing import (
    create_patches,
    crop_image,
    pad_image,
    remove_padding,
    unpatch_image,
)
from cv2_group.models.model_definitions import load_trained_model
from cv2_group.utils.binary import ensure_binary_mask
from cv2_group.utils.configuration import PATCH_SIZE
from cv2_group.utils.predicting import predict_root


@st.cache_resource
def get_model():
    """
    Load and cache the trained model from Azure Model Registry.

    Returns
    -------
    keras.Model
        The trained model loaded from Azure, cached for reuse.
    """
    return load_trained_model()


def analyze_image(image_path: str, model):
    """
    Perform root segmentation on a plant root image.

    Parameters
    ----------
    image_path : str
        Path to the input image file.
    model : keras.Model
        Trained model used for prediction.

    Returns
    -------
    cropped_image : np.ndarray
        The cropped version of the original input image.
    binary_mask : np.ndarray
        A binary segmentation mask indicating predicted root locations.
    """
    image = load_image(image_path)
    cropped_image = crop_image(image)
    padded_image, (top, bottom, left, right) = pad_image(cropped_image, PATCH_SIZE)
    patches, i, j, rgb_image = create_patches(padded_image, PATCH_SIZE)

    preds = predict_root(patches, model)
    predicted_mask = unpatch_image(preds, i, j, rgb_image, PATCH_SIZE)
    predicted_mask_cropped = remove_padding(predicted_mask, top, bottom, left, right)
    binary_mask = ensure_binary_mask(predicted_mask_cropped)

    return cropped_image, binary_mask
'''
