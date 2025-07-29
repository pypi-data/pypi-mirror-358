import base64
import json
import logging
import os
import random
import time
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import requests
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img

from cv2_group.utils.azure_model_loader import load_model_from_azure_registry
from cv2_group.utils.helpers import f1, precision, recall, unpack_model_response

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define custom objects for model loading
CUSTOM_OBJECTS = {
    "f1": f1,
    "precision": precision,
    "recall": recall,
}

# --- Training History Visualization Functions ---


def print_best_val_metrics(history: tf.keras.callbacks.History) -> None:
    """
    Print the best validation loss and F1-score from training history.

    Args:
        history (tf.keras.callbacks.History):
            Keras History object from model.fit().
    """
    best_val_loss = min(history.history["val_loss"])
    best_val_f1 = max(history.history["val_f1"])
    logger.info(f"Best validation loss: {best_val_loss:.4f}")
    logger.info(f"Best validation F1: {best_val_f1:.4f}")


def plot_loss(
    history: tf.keras.callbacks.History, save_path: str = "loss_plot.png"
) -> None:
    """
    Plot and save the training and validation loss curves.

    Args:
        history (tf.keras.callbacks.History):
            Keras History object from model.fit().
        save_path (str):
            Path to save the output loss plot image.
    """
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    epochs = np.arange(1, len(loss) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, loss, label="train_loss")
    plt.plot(epochs, val_loss, label="val_loss")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("Loss (binary_crossentropy)")
    plt.title("Training and Validation Loss")
    plt.xticks(np.arange(1, len(loss) + 1, 3))
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_f1(
    history: tf.keras.callbacks.History, save_path: str = "f1_plot.png"
) -> None:
    """
    Plot and save the training and validation F1-score curves.

    Args:
        history (tf.keras.callbacks.History):
            Keras History object from model.fit().
        save_path (str):
            Path to save the output F1-score plot image.
    """
    train_f1 = history.history["f1"]
    val_f1 = history.history["val_f1"]
    epochs = np.arange(1, len(train_f1) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, train_f1, label="train_f1")
    plt.plot(epochs, val_f1, label="val_f1")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("F1 Score")
    plt.title("Training and Validation F1-Score")
    plt.xticks(np.arange(1, len(train_f1) + 1, 3))
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


# --- Data Loading and Preprocessing Functions ---


def load_images_and_masks(
    image_dir: str, mask_dir: str, patch_size: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load and preprocess images and masks from directories.

    Args:
        image_dir (str): Directory containing input images.
        mask_dir (str): Directory containing corresponding masks.
        patch_size (int): Target size to resize (H, W) of each image and mask.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Arrays of normalized images and masks.
    """
    # Collect image and mask file names
    image_files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith((".png", ".jpg", ".jpeg"))]
    )
    mask_files = sorted(
        [f for f in os.listdir(mask_dir) if f.endswith((".png", ".jpg", ".jpeg"))]
    )

    # Basic checks
    if not image_files or not mask_files:
        raise ValueError(f"No image or mask files found in {image_dir} or {mask_dir}")
    if len(image_files) != len(mask_files):
        logger.warning(
            "Number of images and masks do not match, proceeding cautiously."
        )

    images = []
    masks = []

    for img_file, mask_file in zip(image_files, mask_files):
        img_path = os.path.join(image_dir, img_file)
        mask_path = os.path.join(mask_dir, mask_file)

        # Load and normalize image
        img = (
            img_to_array(load_img(img_path, target_size=(patch_size, patch_size)))
            / 255.0
        )

        # Load and normalize mask (grayscale, binary)
        mask = np.round(
            img_to_array(
                load_img(
                    mask_path,
                    target_size=(patch_size, patch_size),
                    color_mode="grayscale",
                )
            )
            / 255.0
        )

        images.append(img)
        masks.append(mask)

    return np.array(images), np.array(masks)


# --- Auxiliary Evaluation Metrics (NumPy based) ---


def pixel_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute pixel-wise accuracy between ground truth and predicted masks.

    Args:
        y_true (np.ndarray): Ground truth binary mask (H, W) or (H, W, 1).
        y_pred (np.ndarray): Predicted binary mask (H, W) or (H, W, 1).

    Returns:
        float: Pixel accuracy (correct pixels / total pixels).
    """
    y_true_flat = y_true.flatten()
    y_pred_flat = y_pred.flatten()

    correct = np.sum(y_true_flat == y_pred_flat)
    total = y_true_flat.size
    return correct / total


def iou_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Intersection over Union (IoU) between binary ground truth
    and predicted masks.

    Args:
        y_true (np.ndarray): Ground truth binary mask, shape (H, W) or (H, W, 1).
        y_pred (np.ndarray): Predicted binary mask, shape (H, W) or (H, W, 1).

    Returns:
        float: IoU score.
    """
    y_true_flat = y_true.flatten()
    y_pred_flat = y_pred.flatten()

    intersection = np.logical_and(y_true_flat, y_pred_flat).sum()
    union = np.logical_or(y_true_flat, y_pred_flat).sum()

    return 1.0 if union == 0 else intersection / union


# --- Model Evaluation Functions ---


def evaluate_model_on_data(
    model_path: str, x_data: np.ndarray, y_data: np.ndarray, nickname: str
) -> dict:
    """
    Evaluate the model on a dataset using multiple thresholds.

    Args:
        model_path (str): Path to Keras model (MLflow format or .h5 directory).
        x_data (np.ndarray): Input images.
        y_data (np.ndarray): Ground truth masks.
        nickname (str): Identifier for logging purposes.

    Returns:
        dict: Metrics for the best-performing threshold based on mean F1-score.
    """
    logger.info(f"Loading model '{nickname}' from {model_path}...")
    model = None
    loaded_successfully = False

    mlflow_root = model_path
    mlflow_nested_path = os.path.join(model_path, "data", "model")

    # Try MLflow model load from root directory
    if os.path.exists(os.path.join(mlflow_root, "MLmodel")):
        try:
            model = mlflow.tensorflow.load_model(mlflow_root)
            logger.info(f"Loaded MLflow model '{nickname}' from: {mlflow_root}")
            loaded_successfully = True
        except Exception as e:
            logger.warning(f"MLflow load failed for '{nickname}' at {mlflow_root}: {e}")
            logger.debug("MLflow load error:", exc_info=True)

    # Fallback: try loading from nested Keras SavedModel path
    if not loaded_successfully and os.path.exists(mlflow_nested_path):
        try:
            model = tf.keras.models.load_model(
                mlflow_nested_path, custom_objects=CUSTOM_OBJECTS
            )
            logger.info(
                f"Keras load succeeded for '{nickname}' at: {mlflow_nested_path}"
            )
            loaded_successfully = True
        except Exception as e:
            logger.warning(f"Keras load failed at {mlflow_nested_path}: {e}")
            logger.debug("Nested Keras load error:", exc_info=True)

    # Final fallback: try loading directly from model_path
    if not loaded_successfully:
        try:
            model = tf.keras.models.load_model(
                model_path, custom_objects=CUSTOM_OBJECTS
            )
            logger.info(
                f"Keras direct load succeeded for '{nickname}' at: {model_path}"
            )
            loaded_successfully = True
        except Exception as e:
            logger.error(f"Could not load model '{nickname}' from: {model_path}. {e}")
            raise

    if model is None:
        logger.error(f"Model '{nickname}' failed to load.")
        raise RuntimeError(f"Model load failed for '{nickname}'.")

    logger.info(f"Predicting using model '{nickname}'...")
    y_pred = model.predict(x_data)

    thresholds = [0.1, 0.3, 0.5, 0.7]
    best_metrics = {}

    for t in thresholds:
        y_pred_bin = (y_pred > t).astype(np.uint8).squeeze()

        ious, accs, f1s = [], [], []

        for i in range(y_data.shape[0]):
            y_true_i = y_data[i].squeeze()
            y_pred_i = y_pred_bin[i]

            ious.append(iou_score(y_true_i, y_pred_i))
            accs.append(pixel_accuracy(y_true_i, y_pred_i))

            f1_val = f1(
                tf.constant(y_true_i, dtype=tf.float32),
                tf.constant(y_pred_i, dtype=tf.float32),
            ).numpy()
            f1s.append(f1_val)

        metrics = {
            "model": nickname,
            "threshold": t,
            "mean_iou": float(np.mean(ious)),
            "mean_accuracy": float(np.mean(accs)),
            "mean_f1": float(np.mean(f1s)),
        }

        logger.info(
            f"Metrics for '{nickname}' @ threshold {t}:\n"
            f"{json.dumps(metrics, indent=2)}"
        )

        if not best_metrics or metrics["mean_f1"] > best_metrics["mean_f1"]:
            best_metrics = metrics

    logger.info(
        f"Best metrics for '{nickname}':\n" f"{json.dumps(best_metrics, indent=2)}"
    )
    return best_metrics


async def load_test(
    api_url: str,
    image_bytes: bytes,
    api_key: str,
    deployment_target: str,
    num_requests: int = 10,
    min_delay: float = 0.1,
    max_delay: float = 0.5,
) -> Dict[str, Any]:
    """
    Perform a load test against a deployed API endpoint by sending multiple POST
    requests with an image payload encoded as base64, measuring response
    performance and success.

    Args:
        api_url (str): The URL of the API endpoint to test.
        image_bytes (bytes): Raw image data in bytes sent in each request.
        api_key (str): API key used for authorization in request headers.
        deployment_target (str): Identifier for the deployment target
        (e.g., model name).
        num_requests (int, optional): Number of POST requests to send. Default 10.
        min_delay (float, optional): Minimum delay (s) between consecutive requests.
            Default is 0.1.
        max_delay (float, optional): Maximum delay (s) between consecutive requests.
            Default is 0.5.

    Returns:
        Dict[str, Any]: Summary of load test results including:
            - "deployment_target": Deployment target identifier.
            - "total_requests": Number of requests attempted.
            - "success_count": Number of successful requests with valid responses.
            - "failure_count": Number of failed requests (network or invalid).
            - "unpack_failure_count": Number of responses failing unpacking.
            - "average_time_s": Average response time in seconds.
            - "max_time_s": Maximum response time recorded.
            - "min_time_s": Minimum response time recorded.
            - "success_rate": Percentage of successful requests.
            - "sample_unpacked_response": Example unpacked response for inspection.

    Raises:
        None explicitly; exceptions during requests are caught and counted as failures.
    """
    response_times = []
    success_count = 0
    failure_count = 0
    unpack_failure_count = 0
    sample_unpacked_response = None

    base64_image = base64.b64encode(image_bytes).decode()
    payload = {"image_data": base64_image}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "azureml-model-deployment": deployment_target,
    }
    timeout_seconds = 300

    for _ in range(num_requests):
        try:
            start_time = time.time()
            response = requests.post(
                api_url, json=payload, headers=headers, timeout=timeout_seconds
            )
            end_time = time.time()
            elapsed = end_time - start_time
            response_times.append(elapsed)
            response.raise_for_status()

            try:
                # Use the mock unpacking function
                unpacked_data = unpack_model_response(response.text)
                if unpacked_data is None:
                    raise ValueError("Failed to unpack response.")

                if sample_unpacked_response is None:
                    sample_unpacked_response = unpacked_data
                success_count += 1
            except Exception:
                unpack_failure_count += 1
                failure_count += 1

        except (requests.exceptions.RequestException, ValueError) as e:
            failure_count += 1
            print(f"Request failed: {e}")  # Log error for debugging

        if _ < num_requests - 1:
            time.sleep(random.uniform(min_delay, max_delay))

    total_reqs = success_count + failure_count
    results = {
        "deployment_target": deployment_target,
        "total_requests": total_reqs,
        "success_count": success_count,
        "failure_count": failure_count,
        "unpack_failure_count": unpack_failure_count,
        "average_time_s": sum(response_times) / len(response_times)
        if response_times
        else 0,
        "max_time_s": max(response_times) if response_times else 0,
        "min_time_s": min(response_times) if response_times else 0,
        "success_rate": (success_count / total_reqs) * 100 if total_reqs > 0 else 0,
        "sample_unpacked_response": sample_unpacked_response,
    }
    return results


def evaluate_local_model_on_data(
    x_data: np.ndarray, y_data: np.ndarray, nickname: str
) -> dict:
    """
    Evaluate the 'local' model (always loaded from Azure Model Registry)
    on a dataset using multiple thresholds.
    Args:
        x_data (np.ndarray): Input images.
        y_data (np.ndarray): Ground truth masks.
        nickname (str): Identifier for logging purposes.
    Returns:
        dict: Metrics for the best-performing threshold based on mean F1-score.
    """
    logger.info(f"Loading 'local' model '{nickname}' from Azure Model Registry...")
    model = load_model_from_azure_registry()
    logger.info(f"Model '{nickname}' loaded from Azure Model Registry.")
    return evaluate_model_on_data_with_model(model, x_data, y_data, nickname)


def evaluate_model_on_data_with_model(
    model, x_data: np.ndarray, y_data: np.ndarray, nickname: str
) -> dict:
    """
    Evaluate a provided model object on a dataset using multiple thresholds.
    Args:
        model: The loaded Keras model.
        x_data (np.ndarray): Input images.
        y_data (np.ndarray): Ground truth masks.
        nickname (str): Identifier for logging purposes.
    Returns:
        dict: Metrics for the best-performing threshold based on mean F1-score.
    """
    logger.info(f"Predicting using model '{nickname}'...")
    y_pred = model.predict(x_data)
    thresholds = [0.1, 0.3, 0.5, 0.7]
    best_metrics = {}
    for t in thresholds:
        y_pred_bin = (y_pred > t).astype(np.uint8).squeeze()
        ious, accs, f1s = [], [], []
        for i in range(y_data.shape[0]):
            y_true_i = y_data[i].squeeze()
            y_pred_i = y_pred_bin[i]
            ious.append(iou_score(y_true_i, y_pred_i))
            accs.append(pixel_accuracy(y_true_i, y_pred_i))
            f1_val = f1(
                tf.constant(y_true_i, dtype=tf.float32),
                tf.constant(y_pred_i, dtype=tf.float32),
            ).numpy()
            f1s.append(f1_val)
        metrics = {
            "model": nickname,
            "threshold": t,
            "mean_iou": float(np.mean(ious)),
            "mean_accuracy": float(np.mean(accs)),
            "mean_f1": float(np.mean(f1s)),
        }
        logger.info(
            f"Metrics for '{nickname}' @ threshold {t}:\n"
            f"{json.dumps(metrics, indent=2)}"
        )
        if not best_metrics or metrics["mean_f1"] > best_metrics["mean_f1"]:
            best_metrics = metrics
    return best_metrics
