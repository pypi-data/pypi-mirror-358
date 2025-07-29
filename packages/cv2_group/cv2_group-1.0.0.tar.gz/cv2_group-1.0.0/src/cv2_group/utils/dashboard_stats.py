import logging
from collections import deque
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Global counters for dashboard
dashboard_stats = {
    "images_processed": 0,
    "masks_reanalyzed": 0,
    "files_downloaded": 0,
    "processing_times": deque(maxlen=100),  # Keep last 100 processing times for average
    "total_processing_time": 0.0,
}


def get_dashboard_stats() -> Dict[str, Any]:
    """
    Retrieve the current dashboard statistics including counts and processing times.

    Returns:
        Dict[str, Any]: Dictionary containing images processed, masks reanalyzed,
            files downloaded, average processing time (seconds), and total
            processing time (seconds).
    """
    avg_processing_time = 0.0
    if dashboard_stats["processing_times"]:
        avg_processing_time = sum(dashboard_stats["processing_times"]) / len(
            dashboard_stats["processing_times"]
        )

    return {
        "images_processed": dashboard_stats["images_processed"],
        "masks_reanalyzed": dashboard_stats["masks_reanalyzed"],
        "files_downloaded": dashboard_stats["files_downloaded"],
        "average_processing_time": round(avg_processing_time, 2),
        "total_processing_time": round(dashboard_stats["total_processing_time"], 2),
    }


def track_download() -> None:
    """
    Increment the count of files downloaded and log the event.
    """
    dashboard_stats["files_downloaded"] += 1
    logger.info("Download tracked successfully")


def track_image_processed(processing_time: float) -> None:
    """
    Track a completed image processing event by incrementing the count,
    updating timing stats,
    and logging.

    Args:
        processing_time (float): Time taken to process the image in seconds.
    """
    dashboard_stats["images_processed"] += 1
    dashboard_stats["processing_times"].append(processing_time)
    dashboard_stats["total_processing_time"] += processing_time
    logger.info(f"Image processing tracked: {processing_time:.2f}s")


def track_mask_reanalyzed(processing_time: float) -> None:
    """
    Track a completed mask reanalysis event by incrementing the count,
    updating timing stats,
    and logging.

    Args:
        processing_time (float): Time taken to reanalyze the mask in seconds.
    """
    dashboard_stats["masks_reanalyzed"] += 1
    dashboard_stats["processing_times"].append(processing_time)
    dashboard_stats["total_processing_time"] += processing_time
    logger.info(f"Mask reanalysis tracked: {processing_time:.2f}s")


def reset_dashboard_stats() -> None:
    """
    Reset all dashboard statistics including counters and timing data,
    and log the reset.
    """
    dashboard_stats["images_processed"] = 0
    dashboard_stats["masks_reanalyzed"] = 0
    dashboard_stats["files_downloaded"] = 0
    dashboard_stats["processing_times"].clear()
    dashboard_stats["total_processing_time"] = 0.0
    logger.info("Dashboard statistics reset")
