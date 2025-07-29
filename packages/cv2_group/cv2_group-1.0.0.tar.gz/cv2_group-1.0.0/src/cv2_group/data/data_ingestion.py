import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import cv2
import numpy as np
from azureml.core import Datastore
from fastapi import UploadFile

# Configure logging
logger = logging.getLogger(__name__)


def load_image(image_path: str) -> np.ndarray:
    """
    Loads an image from the given file path and converts it to grayscale.

    Parameters
    ----------
    image_path : str
        The path to the image file to be loaded.

    Returns
    -------
    np.ndarray
        The grayscale image as a 2D NumPy array.

    Raises
    ------
    FileNotFoundError
        If the image could not be loaded from the specified path.
    """
    logging.info(f"Attempting to load image from path: {image_path}")

    # Load the image in grayscale
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if the image was loaded correctly
    if grayscale_image is None:
        logging.error(f"Failed to load image from path: {image_path}")
        raise FileNotFoundError(f"Could not load the image at {image_path}")

    logging.info(f"Image successfully loaded from path: {image_path}")
    return grayscale_image


def upload_data(
    images: List[UploadFile], masks: List[UploadFile]
) -> Dict[str, Tuple[UploadFile, UploadFile]]:
    """
    Pair uploaded image and mask files based on matching base filenames.

    Parameters
    ----------
    images : List[UploadFile]
        List of uploaded image files (FastAPI UploadFile objects).
    masks : List[UploadFile]
        List of uploaded mask files (FastAPI UploadFile objects).

    Returns
    -------
    Dict[str, Tuple[UploadFile, UploadFile]]
        Dictionary mapping base filename to (image, mask) tuple.
    """
    logger.info("Pairing uploaded images and masks by base filename.")

    def get_image_key(file: UploadFile) -> str:
        return os.path.splitext(os.path.basename(file.filename))[0]

    def get_mask_key(file: UploadFile) -> str:
        base = os.path.splitext(os.path.basename(file.filename))[0]
        if base.endswith("_root_mask"):
            base = base[: -len("_root_mask")]
        return base

    image_map = {get_image_key(f): f for f in images}
    mask_map = {get_mask_key(f): f for f in masks}

    matched_keys = sorted(set(image_map) & set(mask_map))

    if not matched_keys:
        logger.warning("No matched image-mask file pairs found.")
        return {}

    logger.info(f"Matched {len(matched_keys)} image-mask pairs.")

    paired = {key: (image_map[key], mask_map[key]) for key in matched_keys}

    logger.debug(f"Paired file map: {paired}")
    return paired


def rename_pairs(
    data: Dict[str, Tuple[UploadFile, UploadFile]]
) -> Dict[str, Tuple[str, str]]:
    """
    Generate new filenames for image and mask pairs using UTC timestamp.

    Naming convention:
    - Images: YMDHS_image_x.png
    - Masks:  YMDHS_image_x_root_mask.tif

    Parameters
    ----------
    data : Dict[str, Tuple[UploadFile, UploadFile]]
        Original image/mask UploadFile pairs.

    Returns
    -------
    Dict[str, Tuple[str, str]]
        Mapping from original keys to (new_image_name, new_mask_name).
    """
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    renamed = {}

    for i, key in enumerate(data.keys(), start=1):
        img_name = f"{now_str}_image_{i}.png"
        mask_name = f"{now_str}_image_{i}_root_mask.tif"
        renamed[key] = (img_name, mask_name)

    return renamed


def upload_to_azure_datastore(
    data: Dict[str, Tuple[UploadFile, UploadFile]],
    renamed: Dict[str, Tuple[str, str]],
    datastore: Datastore,
    image_folder: str = "raw_img_final",
    mask_folder: str = "raw_mask_final",
) -> Dict[str, Tuple[str, str]]:
    """
    Save uploaded image and mask files locally with new names and upload them to
    AzureML Datastore under specified folder structure.

    Parameters
    ----------
    data : Dict[str, Tuple[UploadFile, UploadFile]]
        Original image/mask UploadFile pairs keyed by some identifier.
    renamed : Dict[str, Tuple[str, str]]
        Mapping of original keys to new (image_name, mask_name).
    datastore : azureml.core.Datastore
        Azure ML datastore to upload files to.
    image_folder : str, optional
        Folder path in datastore for images (default: "new_v1/raw_img/").
    mask_folder : str, optional
        Folder path in datastore for masks (default: "new_v1/raw_masks/").

    Returns
    -------
    Dict[str, Tuple[str, str]]
        Mapping from original keys to full datastore paths for image and mask.
    """
    logger.info("Uploading renamed files to AzureML Datastore.")
    uploaded_paths = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        for key, (img_file, mask_file) in data.items():
            new_img_name, new_mask_name = renamed[key]

            img_path = os.path.join(tmp_dir, new_img_name)
            mask_path = os.path.join(tmp_dir, new_mask_name)

            # Save image to temp file
            with open(img_path, "wb") as f:
                shutil.copyfileobj(img_file.file, f)

            # Save mask to temp file
            with open(mask_path, "wb") as f:
                shutil.copyfileobj(mask_file.file, f)

            # Upload image to Azure
            datastore.upload_files(
                files=[img_path],
                target_path=image_folder,
                overwrite=True,
                show_progress=False,
            )

            # Upload mask to Azure
            datastore.upload_files(
                files=[mask_path],
                target_path=mask_folder,
                overwrite=True,
                show_progress=False,
            )

            # Store the Azure datastore paths for reference
            uploaded_paths[key] = (
                os.path.join(image_folder, new_img_name),
                os.path.join(mask_folder, new_mask_name),
            )

            logger.debug(f"Uploaded image: {img_path} to {image_folder}")
            logger.debug(f"Uploaded mask: {mask_path} to {mask_folder}")

    logger.info(f"Uploaded {len(uploaded_paths)} image-mask pairs to datastore.")
    return uploaded_paths
