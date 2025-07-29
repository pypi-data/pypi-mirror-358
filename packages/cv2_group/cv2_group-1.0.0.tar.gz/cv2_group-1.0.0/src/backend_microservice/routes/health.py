from fastapi import APIRouter

from cv2_group.utils.dashboard_stats import get_dashboard_stats, track_download

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "ok"}


@router.get("/dashboard/stats")
def get_dashboard_stats_endpoint():
    """Get dashboard statistics."""
    return get_dashboard_stats()


@router.post("/dashboard/track-download")
def track_download_endpoint():
    """Track a file download."""
    track_download()
    return {"message": "Download tracked successfully"}
