import logging
import os
from typing import Tuple

import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import (
    ImageDataGenerator,
    img_to_array,
    load_img,
)

from cv2_group.models.model_definitions import load_model_from_azure_registry
from cv2_group.utils.helpers import f1

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


def load_and_prepare_model_for_retraining(
    learning_rate: float = 1e-5,
    model_name: str = None,
) -> Model:
    """
    Loads the latest version of a U-Net model from the Azure ML Model Registry
    and compiles it for retraining.

    Args:
        learning_rate (float): Learning rate for the optimizer.
        model_name (str): Name of the registered Keras model in Azure ML.

    Returns:
        Model: Compiled U-Net model.

    Raises:
        ValueError: If model_name is not provided.
        Exception: If model fails to load from Azure ML.
    """
    if not model_name:
        raise ValueError(
            "model_name must be provided to load a model from Azure ML Model Registry."
        )

    model_label = "latest"
    logger.info(
        f"Loading model '{model_name}' with label '{model_label}' "
        "from Azure ML Model Registry..."
    )
    try:
        model = load_model_from_azure_registry(
            model_name=model_name,
            model_label=model_label,
        )
    except Exception as e:
        logger.error(f"Failed to load model from Azure ML Registry: {e}")
        raise

    logger.info("Compiling model with Adam optimizer and loss/metrics.")
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", f1],
    )
    return model


def load_image_mask_arrays(
    image_dir: str, mask_dir: str, patch_size: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loads and processes images and corresponding masks.

    Args:
        image_dir (str): Directory with input images.
        mask_dir (str): Directory with corresponding masks.
        patch_size (int): Size to resize images/masks.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Image and mask arrays.
    """
    logger.info(f"Loading images from: {image_dir}")
    logger.info(f"Loading masks from: {mask_dir}")

    image_filenames = sorted(os.listdir(image_dir))
    mask_filenames = sorted(os.listdir(mask_dir))

    image_paths = [os.path.join(image_dir, fname) for fname in image_filenames]
    mask_paths = [os.path.join(mask_dir, fname) for fname in mask_filenames]

    images = [
        img_to_array(load_img(p, target_size=(patch_size, patch_size))) / 255.0
        for p in image_paths
    ]

    masks = [
        np.round(
            img_to_array(
                load_img(
                    p, target_size=(patch_size, patch_size), color_mode="grayscale"
                )
            )
            / 255.0
        )
        for p in mask_paths
    ]

    logger.info(
        f"Loaded {len(images)} images and {len(masks)} masks. "
        f"Mask stats — Min: {np.min(masks)}, Max: {np.max(masks)}, "
        f"Unique: {np.unique(masks)}"
    )

    return np.array(images), np.array(masks)


def create_data_generators(
    patch_size: int,
    train_image_path: str,
    train_mask_path: str,
    val_image_path: str,
    val_mask_path: str,
    batch_size: int = 32,
):
    """
    Creates data generators for training and validation.

    Args:
        patch_size (int): Target patch size.
        train_image_path (str): Path to training images.
        train_mask_path (str): Path to training masks.
        val_image_path (str): Path to validation images.
        val_mask_path (str): Path to validation masks.
        batch_size (int): Batch size.

    Returns:
        tuple: Training and validation generators.
    """
    logger.info("Creating training and validation generators...")
    train_images, train_masks = load_image_mask_arrays(
        train_image_path, train_mask_path, patch_size
    )
    val_images, val_masks = load_image_mask_arrays(
        val_image_path, val_mask_path, patch_size
    )

    train_image_datagen = ImageDataGenerator()
    train_mask_datagen = ImageDataGenerator()
    val_image_datagen = ImageDataGenerator()
    val_mask_datagen = ImageDataGenerator()

    train_image_gen = train_image_datagen.flow(
        train_images, batch_size=batch_size, seed=42, shuffle=True
    )
    train_mask_gen = train_mask_datagen.flow(
        train_masks, batch_size=batch_size, seed=42, shuffle=True
    )
    test_image_gen = val_image_datagen.flow(
        val_images, batch_size=batch_size, seed=42, shuffle=False
    )
    test_mask_gen = val_mask_datagen.flow(
        val_masks, batch_size=batch_size, seed=42, shuffle=False
    )

    logger.info("Data generators created successfully.")

    train_generator = zip(train_image_gen, train_mask_gen)
    test_generator = zip(test_image_gen, test_mask_gen)

    return train_generator, test_generator, train_image_gen, test_image_gen


def train_unet_model(
    model: Model,
    train_generator,
    test_generator,
    train_image_generator,
    test_image_generator,
    epochs: int = 1,
):
    """
    Trains the U-Net model.

    Args:
        model (Model): U-Net model.
        train_generator: Training data.
        test_generator: Validation data.
        train_image_generator: Training image generator.
        test_image_generator: Validation image generator.
        epochs (int): Number of epochs.

    Returns:
        History: Keras training history.
    """
    logger.info(f"Starting training for {epochs} epoch(s)...")
    history = model.fit(
        train_generator,
        steps_per_epoch=len(train_image_generator),
        epochs=epochs,
        validation_data=test_generator,
        validation_steps=len(test_image_generator),
    )
    logger.info("Training complete.")
    return history
