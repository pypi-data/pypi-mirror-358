import numpy as np


def ensure_binary_mask(mask: np.ndarray, threshold: float = 0.3) -> np.ndarray:
    """
    Converts a mask to binary format (values 0 or 255).

    Parameters
    ----------
    mask : np.ndarray
        Input mask, expected to be float (0-1) or int.
    threshold : float
        Threshold to binarize the mask if it's in float format.

    Returns
    -------
    np.ndarray
        Binary mask with dtype uint8 and values 0 or 255.
    """
    if mask.dtype == np.float32 or mask.dtype == np.float64:
        binary_mask = (mask >= threshold).astype(np.uint8) * 255
    elif mask.max() == 1:
        binary_mask = mask.astype(np.uint8) * 255
    elif mask.max() == 255:
        binary_mask = mask.astype(np.uint8)
    else:
        raise ValueError(
            "Unexpected mask range or type. Normalize to 0-1 or 0-255 first."
        )

    return binary_mask
