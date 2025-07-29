from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RoiInput(BaseModel):
    """
    Pydantic model for defining a Region of Interest (ROI).
    """

    x: int = Field(..., description="X-coordinate of the top-left corner of the ROI.")
    y: int = Field(..., description="Y-coordinate of the top-left corner of the ROI.")
    width: int = Field(..., description="Width of the ROI.")
    height: int = Field(..., description="Height of the ROI.")


class RootAnalysisResult(BaseModel):
    """
    Pydantic model for the analysis results of a single root.
    """

    length: float = Field(
        ..., description="Calculated length of the primary root path in pixels."
    )
    tip_coords: Optional[List[int]] = Field(
        None, description="[row, col] coordinates of the root tip."
    )
    base_coords: Optional[List[int]] = Field(
        None, description="[row, col] coordinates of the root base."
    )
    primary_path: Optional[List[List[int]]] = Field(
        None,
        description="List of [row, col] coordinates forming the primary root path.",
    )
    stats: Optional[Dict[str, Any]] = Field(
        None, description="Dictionary of root statistics (e.g., area, bounding box)."
    )


class RootAnalysisItem(BaseModel):
    """
    Combines ROI definition with its corresponding analysis results.
    """

    roi_definition: RoiInput = Field(
        ..., description="Definition of the Region of Interest."
    )
    analysis: RootAnalysisResult = Field(
        ..., description="Analysis results for the root within this ROI."
    )


class RootPredictionResponse(BaseModel):
    """
    Pydantic model for the response from the root prediction and analysis endpoint.
    """

    message: str = Field(
        ..., description="A status message for the prediction request."
    )
    original_image: str = Field(..., description="Base64 encoded original image.")
    full_size_overlay_image: Optional[str] = Field(
        None, description="Base64 encoded full-size image with mask and ROIs overlaid."
    )
    full_size_mask_image: Optional[str] = Field(
        None, description="Base64 encoded full-size predicted mask image."
    )
    full_size_rois_image: Optional[str] = Field(
        None, description="Base64 encoded full-size image with only ROIs drawn."
    )
    full_size_tip_base_image: Optional[str] = Field(
        None, description="Base64 encoded full-size image with tip and base marked."
    )
    # Removed: cropped_rois_image, cropped_overlay_image, cropped_tip_base_image
    root_analysis_results: List[RootAnalysisItem] = Field(
        ...,
        description="List of detailed analysis results"
        "for each identified root in ROIs.",
    )


class ReanalysisRequest(BaseModel):
    """
    Pydantic model for the request to reanalyze an image with edited mask and ROIs.
    """

    original_image_data: str = Field(
        ..., description="Base64 encoded original image data."
    )
    edited_mask_data: str = Field(..., description="Base64 encoded edited mask data.")
    edited_rois: List[RoiInput] = Field(
        ..., description="List of user-defined ROIs for reanalysis."
    )
