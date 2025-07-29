import logging
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from skimage.graph import route_through_array
from skimage.morphology import skeletonize

from cv2_group.models.pydantic_models import (
    RoiInput,
    RootAnalysisItem,
    RootAnalysisResult,
)

logger = logging.getLogger(__name__)


def process_predicted_mask(
    predicted_mask: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray, np.ndarray]:
    """
    Process a binary mask to generate labeled root instances
    using connected components analysis. This function is designed to
    accept masks from both model prediction and user edits.

    Parameters
    ----------
    predicted_mask : np.ndarray
        Input mask (2D array), values can be 0 or 1, or 0-255.
        It will be normalized to 0 or 255 (uint8) for processing.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, int, np.ndarray, np.ndarray]
        - binary_mask: The input mask ensured to be 0/255 uint8.
        - label_ids: Labeled connected components.
        - total_labels: Total number of labels found.
        - stats: Statistics for each connected component.
        - centroids: Centroids for each connected component.
    """
    # Ensure binary_mask is uint8 and 0 or 255
    if predicted_mask.dtype != np.uint8 or predicted_mask.max() == 1:
        binary_mask = (predicted_mask * 255).astype(np.uint8)
    else:
        binary_mask = predicted_mask.copy()

    # Always use connected components for labeling
    retval, label_ids, stats, centroids = cv2.connectedComponentsWithStats(binary_mask)
    total_labels = retval

    return binary_mask, label_ids, total_labels, stats, centroids


def find_labels_in_rois(
    label_ids: np.ndarray,
    total_labels: int,
    stats: np.ndarray,
    rois: List[Tuple[int, int, int, int]],
) -> Tuple[Dict[str, Optional[int]], List[int]]:
    """
    Identify root labels within defined regions of interest (ROIs).
    Prioritizes the label with the maximum height within each ROI.
    Handles cases where no ROIs are provided, returning no specific labels.

    Parameters
    ----------
    label_ids : np.ndarray
        Array with labeled connected components.
    total_labels : int
        Total number of labels found.
    stats : np.ndarray
        Statistics for each connected component.
    rois : List[Tuple[int, int, int, int]]
        List of ROIs, each as (x, y, width, height).

    Returns
    -------
    Tuple[Dict[str, Optional[int]], List[int]]
        - max_label_dict: Dictionary mapping "label_idx" to the identified
                          label ID, or None if no label found in ROI.
        - max_label_list: List of identified label IDs (can contain None).
    """
    max_label_dict = {}
    max_label_list = []

    # This function expects ROIs to be provided.
    # If no ROIs, the calling function (_perform_root_analysis)
    # should handle how to proceed.
    if not rois:
        logger.warning(
            "`find_labels_in_rois` called with no ROIs. "
            "This might indicate an issue in the calling logic."
        )
        return max_label_dict, max_label_list

    for counter, roi in enumerate(rois):
        key = f"label_{counter}"
        x, y, width, height = roi
        x_end, y_end = x + width, y + height

        indices_in_roi = []
        for i in range(1, total_labels):  # Skip background label (0)
            if i >= stats.shape[0]:
                logger.warning(
                    f"Label ID {i} out of bounds for stats array "
                    f"(shape {stats.shape}). Skipping."
                )
                continue

            label_x = stats[i, cv2.CC_STAT_LEFT]
            label_y = stats[i, cv2.CC_STAT_TOP]
            label_width = stats[i, cv2.CC_STAT_WIDTH]
            label_height = stats[i, cv2.CC_STAT_HEIGHT]
            label_x_end = label_x + label_width
            label_y_end = label_y + label_height

            # Check for intersection between ROI and label bounding box
            if not (
                x_end < label_x or label_x_end < x or y_end < label_y or label_y_end < y
            ):
                indices_in_roi.append(i)

        if indices_in_roi:
            # Find the label with the maximum height within the ROI
            max_height_label = max(
                indices_in_roi, key=lambda idx: stats[idx, cv2.CC_STAT_HEIGHT]
            )
            max_label_list.append(max_height_label)
            max_label_dict[key] = max_height_label
            logger.info(
                f"ROI {roi}: Label {max_height_label} has the highest "
                f"height: {stats[max_height_label, cv2.CC_STAT_HEIGHT]}"
            )
        else:
            max_label_dict[key] = None
            logger.info(f"ROI {roi}: No labels found.")

    return max_label_dict, max_label_list


def extract_root_instances(
    label_ids: np.ndarray, max_label_ids_for_rois: List[Optional[int]]
) -> List[Optional[np.ndarray]]:
    """
    Extract binary masks for individual root instances from a labeled image.
    Each extracted mask will have values 0 or 1.

    Parameters
    ----------
    label_ids : np.ndarray
        Array with labeled connected components.
    max_label_ids_for_rois : List[Optional[int]]
        List of label IDs to extract, corresponding to identified ROIs.
        Can contain None for ROIs where no label was found.

    Returns
    -------
    List[Optional[np.ndarray]]
        List of binary masks (0 or 1) for each root instance, or None if no
        instance was found for a given ROI.
    """
    root_instances = []
    for label_id in max_label_ids_for_rois:
        if label_id is not None and label_id != 0:
            # Create a binary mask (0 or 1) for the specific label
            label_mask = np.where(label_ids == label_id, 1, 0).astype(np.uint8)
            root_instances.append(label_mask)
        else:
            root_instances.append(None)
    return root_instances


def _get_skeleton_tip_base(
    root_mask: np.ndarray,
) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]], np.ndarray]:
    """
    Generates the skeleton from a binary root mask and identifies
    the tip and base coordinates.
    The tip is defined as the lowest point (max row), and the base
    as the highest point (min row) on the skeleton.

    Parameters
    ----------
    root_mask : np.ndarray
        A 2D binary mask (0 or 1) of a single root instance.

    Returns
    -------
    Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]], np.ndarray]
        - base_coords: (row, col) of the root base, or None if no skeleton.
        - tip_coords: (row, col) of the root tip, or None if no skeleton.
        - skeleton: The skeletonized mask (binary 0 or 1).
    """
    skeleton = skeletonize(root_mask)

    if not np.any(skeleton):
        logger.error("Skeleton contains no valid pixels.")
        return None, None, skeleton

    coords = np.where(skeleton > 0)
    # coords[0] are rows (y), coords[1] are columns (x)

    # Find the top-most (min row) and bottom-most (max row) points
    min_row_idx = np.argmin(coords[0])
    max_row_idx = np.argmax(coords[0])

    base = (coords[0][min_row_idx], coords[1][min_row_idx])
    tip = (coords[0][max_row_idx], coords[1][max_row_idx])

    return base, tip, skeleton


def _calculate_path_length(
    skeleton: np.ndarray,
    base: Tuple[int, int],
    tip: Tuple[int, int],
    log_prefix: str = "",
) -> Tuple[float, Optional[List[List[int]]]]:
    """
    Calculates the primary root path and its length using Dijkstra's algorithm
    on the skeletonized mask.

    Parameters
    ----------
    skeleton : np.ndarray
        The skeletonized binary mask (0 or 1).
    base : Tuple[int, int]
        Coordinates [row, col] of the root base.
    tip : Tuple[int, int]
        Coordinates [row, col] of the root tip.
    log_prefix : str
        Prefix for logging messages to identify the current root instance.

    Returns
    -------
    Tuple[float, Optional[List[List[int]]]]
        - length: Euclidean length of the primary root path in pixels.
        - primary_path: List of [row, col] coordinates forming the path.
                        Returns None if pathfinding fails.
    """
    if base == tip:
        logger.warning(
            f"{log_prefix}: Base and Tip are identical or very close. "
            f"Length will be 0."
        )
        return 0.0, [list(base)] if base else []

    # Assign a cost of 1 to skeleton pixels, high cost to background
    costs = np.where(skeleton, 1, 1_000_000)

    try:
        path_coords, _ = route_through_array(
            costs, start=base, end=tip, fully_connected=True
        )
        path_coords = np.array(path_coords)

        # Calculate Euclidean length of the path
        length = np.sum(np.sqrt(np.sum(np.diff(path_coords, axis=0) ** 2, axis=1)))

        return float(length), path_coords.tolist()
    except Exception as e:
        logger.error(
            f"{log_prefix}: Pathfinding failed with error: {e}. "
            "Returning length 0 and no path."
        )
        return 0.0, None


def analyze_primary_root(
    root_instances: List[Optional[np.ndarray]],
    original_roi_indices: List[int],
) -> List[Dict[str, Any]]:
    """
    Analyze each primary root binary mask instance to extract geometric and path
    features.

    Parameters
    ----------
    root_instances : list of np.ndarray or None
        List of binary masks representing individual root instances.
        Elements can be None if no root was detected.
    original_roi_indices : list of int
        Indices mapping each root instance back to the original ROI.

    Returns
    -------
    list of dict
        Each dict contains:
            - 'roi_index' (int): ROI index for this root.
            - 'length' (float): Length of the primary root path.
            - 'tip_coords' (list or None): Coordinates [y, x] of the root tip.
            - 'base_coords' (list or None): Coordinates [y, x] of the root base.
            - 'primary_path' (list or None): List of coordinates of the primary root.
    """
    results = []

    for i, root in enumerate(root_instances):
        log_prefix = (
            f"Root instance {i} (original ROI index " f"{original_roi_indices[i]})"
        )

        # Initialize result_entry with defaults, including length
        result_entry: Dict[str, Any] = {
            "roi_index": original_roi_indices[i],
            "length": 0.0,
            "tip_coords": None,
            "base_coords": None,
            "primary_path": None,
        }

        if root is None:
            logger.info(f"{log_prefix} is None. Skipping analysis.")
            results.append(result_entry)
            continue

        logger.info(f"Analyzing {log_prefix}.")

        base, tip, skeleton = _get_skeleton_tip_base(root)

        if base is None or tip is None:
            logger.error(
                f"{log_prefix}: Could not determine tip/base. "
                "Skipping path analysis."
            )
            results.append(result_entry)
            continue

        length, primary_path = _calculate_path_length(skeleton, base, tip, log_prefix)

        result_entry.update(
            {
                "length": length,
                "tip_coords": list(tip) if tip else None,
                "base_coords": list(base) if base else None,
                "primary_path": primary_path,
            }
        )
        results.append(result_entry)

    logger.info("Finished analyzing all root instances.")
    return results


def _perform_root_analysis(
    binary_mask: np.ndarray,
    rois_for_analysis: List[Tuple[int, int, int, int]],
    rois_input_for_response: List[RoiInput],
    original_roi_indices: List[int],
) -> List[RootAnalysisItem]:
    """
    Extract root instances from a binary mask and perform primary root analysis
    for each ROI.

    Parameters
    ----------
    binary_mask : np.ndarray
        Binary mask array representing segmented roots.
    rois_for_analysis : list of tuple of int
        List of bounding box ROIs (ymin, xmin, ymax, xmax) to analyze in the mask.
    rois_input_for_response : list of RoiInput
        ROI input models used to build the final analysis response.
    original_roi_indices : list of int
        Original indices corresponding to each ROI.

    Returns
    -------
    list of RootAnalysisItem
        Analysis results for each ROI, including extracted root metrics and stats.

    Notes
    -----
    This function expects `rois_for_analysis` to be non-empty; empty list handling
    should be done upstream.
    """
    if not rois_for_analysis:
        logger.error(
            "'_perform_root_analysis' called without ROIs. "
            "This should be handled by the calling function (app.py)."
        )
        # Fallback to empty list, as app.py should prevent this case
        return []

    # Connected components analysis is always performed directly
    _, label_ids, total_labels, stats, centroids = process_predicted_mask(binary_mask)

    max_label_dict, _ = find_labels_in_rois(
        label_ids, total_labels, stats, rois_for_analysis
    )

    # Create an ordered list of labels to extract based on provided ROIs
    labels_to_extract_ordered = []
    for i in range(len(rois_input_for_response)):
        labels_to_extract_ordered.append(max_label_dict.get(f"label_{i}"))

    root_instances_ordered = extract_root_instances(
        label_ids, labels_to_extract_ordered
    )

    analysis_results_raw = analyze_primary_root(
        root_instances_ordered, original_roi_indices
    )

    final_analysis_data: List[RootAnalysisItem] = []
    for i, roi_input_model in enumerate(rois_input_for_response):
        # Always start with valid defaults for RootAnalysisResult
        current_analysis_data: Dict[str, Any] = {
            "length": 0.0,
            "tip_coords": None,
            "base_coords": None,
            "primary_path": None,
            "stats": None,
        }

        result_for_roi = next(
            (res for res in analysis_results_raw if res.get("roi_index") == i), None
        )

        if result_for_roi:
            # Only update if an actual analysis result was found
            analysis_copy = result_for_roi.copy()
            analysis_copy.pop("roi_index", None)
            current_analysis_data.update(analysis_copy)

            label_id_in_roi = max_label_dict.get(f"label_{i}")
            if (
                label_id_in_roi is not None
                and label_id_in_roi != 0
                and label_id_in_roi < stats.shape[0]
            ):
                roi_stats = {
                    "area": int(stats[label_id_in_roi, cv2.CC_STAT_AREA]),
                    "left": int(stats[label_id_in_roi, cv2.CC_STAT_LEFT]),
                    "top": int(stats[label_id_in_roi, cv2.CC_STAT_TOP]),
                    "width": int(stats[label_id_in_roi, cv2.CC_STAT_WIDTH]),
                    "height": int(stats[label_id_in_roi, cv2.CC_STAT_HEIGHT]),
                    "centroid_x": float(centroids[label_id_in_roi, 0]),
                    "centroid_y": float(centroids[label_id_in_roi, 1]),
                }
                current_analysis_data["stats"] = roi_stats
            else:
                current_analysis_data["stats"] = None
        else:
            logger.info(
                f"No analysis result found for ROI index {i}. "
                "Using default analysis data."
            )

        final_analysis_data.append(
            RootAnalysisItem(
                roi_definition=roi_input_model,
                analysis=RootAnalysisResult(**current_analysis_data),
            )
        )
    return final_analysis_data
