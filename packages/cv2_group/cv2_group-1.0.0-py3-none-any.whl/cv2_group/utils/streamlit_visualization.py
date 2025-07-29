'''
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def display_predicted_mask(pred_mask: np.ndarray) -> plt.Figure:
    """
    Generate a matplotlib figure displaying a predicted binary mask.

    Parameters
    ----------
    pred_mask : np.ndarray
        The predicted binary mask to be displayed. Can be 2D or 3D with a
        singleton dimension.

    Returns
    -------
    fig : matplotlib.figure.Figure
        A matplotlib figure containing the mask visualization.
    """
    if pred_mask.ndim == 3 and pred_mask.shape[-1] == 1:
        pred_mask = pred_mask[..., 0]
    elif pred_mask.ndim == 3 and pred_mask.shape[0] == 1:
        pred_mask = pred_mask[0]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title("Predicted Mask")
    ax.imshow(pred_mask, cmap="gray")
    ax.axis("off")
    return fig


def display_overlay_image(
    cropped_image: np.ndarray, predicted_mask: np.ndarray, alpha: float = 0.5
) -> Image.Image:
    """
    Create an overlay image showing predicted roots in red on top of the original input.

    Parameters
    ----------
    cropped_image : np.ndarray
        The original cropped input image, either grayscale or RGB.
    predicted_mask : np.ndarray
        The predicted binary mask of the same spatial dimensions as the image.
    alpha : float, optional
        Transparency factor for the overlay; 0.0 means only original image,
        1.0 means only the red mask. Default is 0.5.

    Returns
    -------
    overlay_image : PIL.Image.Image
        The resulting overlay image in RGB format.
    """
    if len(cropped_image.shape) == 2:
        original_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2BGR)
    else:
        original_rgb = cropped_image.copy()

    red_mask = np.zeros_like(original_rgb)
    red_mask[..., 2] = predicted_mask
    overlay = cv2.addWeighted(original_rgb, 1 - alpha, red_mask, alpha, 0)

    overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    return Image.fromarray(overlay_rgb)
'''
