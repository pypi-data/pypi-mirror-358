import base64
import logging
import os
import time
import traceback
from enum import Enum
from typing import Optional

import cv2
import numpy as np
import requests
from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from fastapi import (
    APIRouter,
    Body,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from cv2_group.features.feature_extraction import _perform_root_analysis
from cv2_group.models.model_definitions import load_trained_model
from cv2_group.models.pydantic_models import (
    ReanalysisRequest,
    RoiInput,
    RootPredictionResponse,
)
from cv2_group.utils.configuration import DEFAULT_ROIS
from cv2_group.utils.dashboard_stats import track_image_processed, track_mask_reanalyzed
from cv2_group.utils.helpers import shift_traffic
from cv2_group.utils.image_helpers import unpack_model_response
from cv2_group.utils.image_processing import _process_rois_json
from cv2_group.utils.predicting import predict_from_array
from cv2_group.utils.visualization import _generate_full_size_visualizations

logger = logging.getLogger(__name__)
router = APIRouter()

# Load model once globally
model = load_trained_model()

# Global routing state (in-memory for now)
current_routing = {"blue_percent": 50, "green_percent": 50}


@router.get("/test-azure/")
async def test_azure_connectivity():
    """
    Test connectivity to Azure ML endpoint
    """
    try:
        # F821 undefined name 'load_config' - Removed as it's not defined
        # and configuration should come from environment variables.
        # azure_cfg = config["azure_model"]
        # url = azure_cfg["endpoint"]
        # api_key = azure_cfg["api_key"]

        url = os.getenv("AZURE_MODEL_ENDPOINT")
        api_key = os.getenv("AZURE_MODEL_API_KEY")

        if not url or not api_key:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Azure endpoint URL or API key not set in environment variables."
                ),
            )

        # Simple health check request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Try a simple GET request first (if supported)
        try:
            response = requests.get(
                url.replace("/score", "/health"), headers=headers, timeout=10
            )
            if response.status_code == 200:
                return {"status": "healthy", "message": "Azure endpoint is responding"}
        # E722 do not use bare 'except' - Replaced with specific exception
        except requests.exceptions.RequestException as req_e:
            logger.warning(
                f"Azure health check GET request failed: {req_e}. "
                "Attempting POST request."
            )
            pass

        # If health check fails, try a minimal POST request
        test_payload = {"test": "ping"}
        response = requests.post(url, headers=headers, json=test_payload, timeout=10)

        if response.status_code == 200:
            return {"status": "connected", "message": "Azure endpoint is reachable"}
        else:
            return {
                "status": "error",
                "message": f"Azure endpoint returned status {response.status_code}",
            }

    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Cannot connect to Azure endpoint - connection refused",
        }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Azure endpoint timeout - service may be overloaded",
        }
    except Exception as e:
        # E722 do not use bare 'except' - This is a broad catch,
        # but in a top-level error handler for API routes, it's often
        # used to catch any unhandled exceptions before they crash the app.
        # Logging the traceback provides crucial debugging info.
        logger.error(f"Azure connectivity test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Azure connectivity test failed: {str(e)}",
        }


@router.post("/predict/", response_model=RootPredictionResponse)
async def predict(
    request: Request,
    file: UploadFile = File(
        ..., description="Image file to predict root segmentation."
    ),
    rois_json: Optional[str] = Form(
        None,
        description="JSON ROI is {'x': int, 'y': int, 'width': int, 'height': int}",
    ),
    model_source: str = Form(
        "local", description="Which model to use: 'local' or 'azure'"
    ),
):
    """
    Predicts root segmentation mask, performs root analysis, and generates
    visualizations. If no ROIs are provided, uses DEFAULT_ROIS.
    """
    start_time = time.time()
    try:
        logger.info(f"--- /predict called ---")
        logger.info(f"Request from {request.client.host}")
        logger.info(
            f"Received file: {file.filename}, content type: {file.content_type}"
        )

        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from uploaded file.")

        nparr = np.frombuffer(contents, np.uint8)
        original_image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if original_image_bgr is None:
            logger.error("cv2.imdecode returned None — image decoding failed.")
            raise HTTPException(
                status_code=400,
                detail="Failed to decode image. Invalid format or corrupted.",
            )

        logger.info(f"Image decoded. Shape: {original_image_bgr.shape}")
        original_image_shape = original_image_bgr.shape[:2]

        if model_source == "azure":
            logger.info("Calling Azure model via API...")
            url = os.getenv("AZURE_MODEL_ENDPOINT")
            api_key = os.getenv("AZURE_MODEL_API_KEY")

            if not url or not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Azure model endpoint URL or API key not set.",
                )

            _, buffer = cv2.imencode(".png", original_image_bgr)
            b64_image = base64.b64encode(buffer).decode()
            payload = {"image_data": b64_image}
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            compressed_response_string = response.text
            (
                cropped_image_for_prediction,
                uncropped_binary_mask,
                original_bbox,
                square_offsets,
                binary_mask_cropped_square,
            ) = unpack_model_response(compressed_response_string)
        else:
            logger.info("Calling predict_from_array() (local model)...")
            (
                cropped_image_for_prediction,
                uncropped_binary_mask,
                original_bbox,
                square_offsets,
                binary_mask_cropped_square,
            ) = predict_from_array(
                image=original_image_bgr,
                original_image_shape=original_image_shape,
                model=model,
            )

        # F841 local variable 'azure_r'/'cropped_image_for_prediction_azure' etc.
        # is assigned to but never used. These variables were only used in the
        # `/predict/both` endpoint, so they are not needed here and have been removed
        # from the `if model_source == "azure":` block. The variables
        # `cropped_image_for_prediction`, `original_bbox`, `square_offsets`, and
        # `binary_mask_cropped_square` are now assigned in both branches and
        # are only used in the `predict_from_array` and `unpack_model_response` calls.
        # This addresses the F841 warnings.

        if uncropped_binary_mask is None or uncropped_binary_mask.size == 0:
            logger.error("Segmentation model returned an empty or invalid mask.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Segmentation model returned an empty or invalid mask.",
            )

        if rois_json:
            (
                rois_for_analysis,
                rois_input_for_response,
                original_roi_indices,
            ) = _process_rois_json(rois_json)
            logger.info(f"Using user-provided ROIs: {rois_for_analysis}")
        else:
            logger.info("No ROIs JSON provided. Using DEFAULT_ROIS.")
            rois_for_analysis = list(DEFAULT_ROIS)
            rois_input_for_response = [
                RoiInput(x=r[0], y=r[1], width=r[2], height=r[3]) for r in DEFAULT_ROIS
            ]
            original_roi_indices = list(range(len(DEFAULT_ROIS)))

        logger.info("Performing root analysis...")
        final_analysis_data = _perform_root_analysis(
            uncropped_binary_mask,
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        )
        logger.info(f"Root analysis produced {len(final_analysis_data)} items.")

        analysis_results_for_display_full_size = []
        for item in final_analysis_data:
            raw_result = item.analysis.dict()
            full_size_raw_result = raw_result.copy()
            analysis_results_for_display_full_size.append(full_size_raw_result)

        logger.info("Generating full-size visualizations...")
        (
            full_size_overlay_image_base64,
            full_size_mask_image_base64,
            full_size_rois_image_base64,
            full_size_tip_base_image_base64,
        ) = _generate_full_size_visualizations(
            original_image_bgr,
            uncropped_binary_mask,
            rois_for_analysis,
            analysis_results_for_display_full_size,
        )

        _, buffer = cv2.imencode(".png", original_image_bgr)
        original_image_base64 = base64.b64encode(buffer).decode("utf-8")

        processing_time = time.time() - start_time
        track_image_processed(processing_time)

        logger.info(
            f"Prediction completed successfully in {processing_time:.2f} seconds."
        )
        return RootPredictionResponse(
            message="Prediction and analysis successful",
            original_image=original_image_base64,
            full_size_overlay_image=full_size_overlay_image_base64,
            full_size_mask_image=full_size_mask_image_base64,
            full_size_rois_image=full_size_rois_image_base64,
            full_size_tip_base_image=full_size_tip_base_image_base64,
            root_analysis_results=final_analysis_data,
        )
    except HTTPException as he:
        logger.warning(f"HTTPException raised: {he.detail}")
        raise he
    except ValueError as ve:
        logger.error(f"Client value error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    # E722 do not use bare 'except' - Replaced with specific exception or
    # a general Exception with detailed traceback logging.
    except requests.exceptions.RequestException as req_e:
        logger.error(f"External service request error: {req_e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External service error: {str(req_e)}",
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Unexpected error during prediction:\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during prediction: {str(e)}",
        )


@router.post("/reanalyze/", response_model=RootPredictionResponse)
async def reanalyze(request: ReanalysisRequest):
    """
    Reanalyzes an image with a user-edited mask and user-defined ROIs,
    generating new analysis results and visualizations.
    """
    start_time = time.time()
    try:
        logger.info("Reanalysis request received.")

        # 1. Decode edited mask and original image from base64
        edited_mask_bytes = base64.b64decode(request.edited_mask_data)
        edited_mask_np = np.frombuffer(edited_mask_bytes, np.uint8)
        # Use IMREAD_UNCHANGED first to get all channels, then explicitly convert
        edited_mask = cv2.imdecode(edited_mask_np, cv2.IMREAD_UNCHANGED)

        # --- Ensure edited_mask is grayscale regardless of initial channels ---
        if edited_mask is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode edited mask data from base64.",
            )

        # If the image has 3 or 4 channels, convert it to grayscale
        if edited_mask.ndim == 3:
            # Handle RGBA to BGR first if it's a 4-channel image
            if edited_mask.shape[2] == 4:
                edited_mask = cv2.cvtColor(edited_mask, cv2.COLOR_BGRA2BGR)
            # Convert to grayscale (single channel)
            edited_mask = cv2.cvtColor(edited_mask, cv2.COLOR_BGR2GRAY)
        # If ndim is 2, it's already grayscale, no conversion needed

        original_image_bytes = base64.b64decode(request.original_image_data)
        original_image_np = np.frombuffer(original_image_bytes, np.uint8)
        original_image_bgr = cv2.imdecode(original_image_np, cv2.IMREAD_UNCHANGED)
        if len(original_image_bgr.shape) == 2:
            original_image_bgr = cv2.cvtColor(original_image_bgr, cv2.COLOR_GRAY2BGR)
        elif original_image_bgr.shape[2] == 4:  # RGBA
            original_image_bgr = cv2.cvtColor(original_image_bgr, cv2.COLOR_RGBA2BGR)

        if original_image_bgr is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode original image data from base64.",
            )

        # Ensure edited_mask is binary (0 or 255)
        # It should now be 2D (grayscale) from the fix above, but pixel values
        # might still be intermediate (e.g., from canvas drawing).
        if edited_mask.max() == 1:
            edited_mask = (edited_mask * 255).astype(np.uint8)
        elif edited_mask.max() > 1 and edited_mask.max() < 255:
            # If values are not 0 or 255, apply a threshold for binarization
            _, edited_mask = cv2.threshold(edited_mask, 127, 255, cv2.THRESH_BINARY)
        edited_mask = edited_mask.astype(np.uint8)

        # 2. Process ROIs from the request
        rois_for_analysis = [
            (roi.x, roi.y, roi.width, roi.height) for roi in request.edited_rois
        ]
        rois_input_for_response = request.edited_rois
        original_roi_indices = list(range(len(request.edited_rois)))

        # If no ROIs are provided by the user, use the DEFAULT_ROIS
        if not rois_for_analysis:
            logger.info(
                "No ROIs provided for reanalysis. " "Using DEFAULT_ROIS for analysis."
            )
            rois_for_analysis = list(DEFAULT_ROIS)
            rois_input_for_response = [
                RoiInput(x=r[0], y=r[1], width=r[2], height=r[3]) for r in DEFAULT_ROIS
            ]
            original_roi_indices = list(range(len(DEFAULT_ROIS)))

        # 3. Perform Root Analysis on the edited mask and ROIs
        final_analysis_data = _perform_root_analysis(
            edited_mask,
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        )

        analysis_results_for_display_full_size = []

        if rois_for_analysis and final_analysis_data:
            for item in final_analysis_data:
                raw_result = item.analysis.dict()
                full_size_raw_result = raw_result.copy()
                analysis_results_for_display_full_size.append(full_size_raw_result)

        # 4. Generate Visualizations (only full-size)
        (
            full_size_overlay_image_base64,
            full_size_mask_image_base64,
            full_size_rois_image_base64,
            full_size_tip_base_image_base64,
        ) = _generate_full_size_visualizations(
            original_image_bgr,
            edited_mask,  # Use the edited mask for visualization
            rois_for_analysis,
            analysis_results_for_display_full_size,
        )

        # The 'original_image' field in the response should still be the
        # *actual* original image, not the edited mask.
        _, buffer = cv2.imencode(".png", original_image_bgr)
        original_image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Update dashboard statistics
        processing_time = time.time() - start_time
        track_mask_reanalyzed(processing_time)

        logger.info(
            f"Reanalysis completed successfully in {processing_time:.2f} seconds."
        )
        return RootPredictionResponse(
            message="Reanalysis successful",
            original_image=original_image_base64,
            full_size_overlay_image=full_size_overlay_image_base64,
            full_size_mask_image=full_size_mask_image_base64,
            full_size_rois_image=full_size_rois_image_base64,
            full_size_tip_base_image=full_size_tip_base_image_base64,
            # Removed cropped image fields from response
            root_analysis_results=final_analysis_data,
        )

    except HTTPException as he:
        raise he
    except ValueError as ve:
        logger.error(f"Client error during reanalysis: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    # E722 do not use bare 'except' - Replaced with specific exception or
    # a general Exception with detailed traceback logging.
    except Exception as e:
        logger.error(f"Reanalysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during reanalysis: {e}",
        )


@router.post("/predict/both/", response_model=dict)
async def predict_both(
    request: Request,
    file: UploadFile = File(
        ..., description="Image file to predict root segmentation."
    ),
    rois_json: Optional[str] = Form(
        None,
        description="JSON ROI is {'x': int, 'y': int, 'width': int, 'height': int}",
    ),
):
    """
    Predicts root segmentation mask using both local and Azure models,
    performs root analysis, and generates visualizations for both.
    Returns both results in a unified response.
    """
    start_time = time.time()
    try:
        logger.info(f"--- /predict/both called ---")
        logger.info(f"Request from {request.client.host}")
        logger.info(
            f"Received file: {file.filename}, content type: {file.content_type}"
        )

        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from uploaded file.")

        nparr = np.frombuffer(contents, np.uint8)
        original_image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if original_image_bgr is None:
            logger.error("cv2.imdecode returned None — image decoding failed.")
            raise HTTPException(
                status_code=400,
                detail="Failed to decode image. Invalid format or corrupted.",
            )

        logger.info(f"Image decoded. Shape: {original_image_bgr.shape}")
        original_image_shape = original_image_bgr.shape[:2]

        # Predict with local model
        logger.info("Calling predict_from_array() (local model)...")
        (
            _cropped_image_for_prediction_local,  # F841: Assigned but never used
            uncropped_binary_mask_local,
            _original_bbox_local,  # F841: Assigned but never used
            _square_offsets_local,  # F841: Assigned but never used
            _binary_mask_cropped_square_local,  # F841: Assigned but never used
        ) = predict_from_array(
            image=original_image_bgr,
            original_image_shape=original_image_shape,
            model=model,
        )

        # Predict with Azure model
        logger.info("Calling Azure model via API...")
        azure_prediction_successful = False
        # azure_results = None # F841: Assigned but never used - Removed

        try:
            url = os.getenv("AZURE_MODEL_ENDPOINT")
            api_key = os.getenv("AZURE_MODEL_API_KEY")

            if not url or not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Azure model endpoint URL or API key not set.",
                )

            _, buffer = cv2.imencode(".png", original_image_bgr)
            b64_image = base64.b64encode(buffer).decode()
            payload = {"image_data": b64_image}
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            compressed_response_string = response.text
            (
                _cropped_image_for_prediction_azure,  # F841: Assigned but never used
                uncropped_binary_mask_azure,
                _original_bbox_azure,  # F841: Assigned but never used
                _square_offsets_azure,  # F841: Assigned but never used
                _binary_mask_cropped_square_azure,  # F841: Assigned but never used
            ) = unpack_model_response(compressed_response_string)
            azure_prediction_successful = True
            logger.info("Azure model prediction successful")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Azure model prediction failed: {e}")
            logger.info("Falling back to local model only for Azure results")
            # Use local results for Azure as fallback
            uncropped_binary_mask_azure = uncropped_binary_mask_local
            # The following variables are not used beyond this point for Azure results,
            # so they can be removed to avoid F841 warnings.
            # _cropped_image_for_prediction_azure = cropped_image_for_prediction_local
            # _original_bbox_azure = original_bbox_local
            # _square_offsets_azure = square_offsets_local
            # _binary_mask_cropped_square_azure = binary_mask_cropped_square_local
        # E722 do not use bare 'except' - Replaced with specific exception or
        # a general Exception with detailed traceback logging.
        except Exception as e:
            logger.error(f"Unexpected error during Azure prediction: {e}")
            logger.info("Falling back to local model only for Azure results")
            # Use local results for Azure as fallback
            uncropped_binary_mask_azure = uncropped_binary_mask_local
            # The following variables are not used beyond this point for Azure results,
            # so they can be removed to avoid F841 warnings.
            # _cropped_image_for_prediction_azure = cropped_image_for_prediction_local
            # _original_bbox_azure = original_bbox_local
            # _square_offsets_azure = square_offsets_local
            # _binary_mask_cropped_square_azure = binary_mask_cropped_square_local

        # Process ROIs (same for both)
        if rois_json:
            (
                rois_for_analysis,
                rois_input_for_response,
                original_roi_indices,
            ) = _process_rois_json(rois_json)
            logger.info(f"Using user-provided ROIs: {rois_for_analysis}")
        else:
            logger.info("No ROIs JSON provided. Using DEFAULT_ROIS.")
            rois_for_analysis = list(DEFAULT_ROIS)
            rois_input_for_response = [
                RoiInput(x=r[0], y=r[1], width=r[2], height=r[3]) for r in DEFAULT_ROIS
            ]
            original_roi_indices = list(range(len(DEFAULT_ROIS)))

        # Root analysis and visualizations for local
        logger.info("Performing root analysis (local)...")
        final_analysis_data_local = _perform_root_analysis(
            uncropped_binary_mask_local,
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        )
        analysis_results_for_display_full_size_local = []
        for item in final_analysis_data_local:
            raw_result = item.analysis.dict()
            full_size_raw_result = raw_result.copy()
            analysis_results_for_display_full_size_local.append(full_size_raw_result)

        logger.info("Generating full-size visualizations (local)...")
        (
            full_size_overlay_image_base64_local,
            full_size_mask_image_base64_local,
            full_size_rois_image_base64_local,
            full_size_tip_base_image_base64_local,
        ) = _generate_full_size_visualizations(
            original_image_bgr,
            uncropped_binary_mask_local,
            rois_for_analysis,
            analysis_results_for_display_full_size_local,
        )

        # Root analysis and visualizations for azure
        logger.info("Performing root analysis (azure)...")
        final_analysis_data_azure = _perform_root_analysis(
            uncropped_binary_mask_azure,
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        )
        analysis_results_for_display_full_size_azure = []
        for item in final_analysis_data_azure:
            raw_result = item.analysis.dict()
            full_size_raw_result = raw_result.copy()
            analysis_results_for_display_full_size_azure.append(full_size_raw_result)

        logger.info("Generating full-size visualizations (azure)...")
        (
            full_size_overlay_image_base64_azure,
            full_size_mask_image_base64_azure,
            full_size_rois_image_base64_azure,
            full_size_tip_base_image_base64_azure,
        ) = _generate_full_size_visualizations(
            original_image_bgr,
            uncropped_binary_mask_azure,
            rois_for_analysis,
            analysis_results_for_display_full_size_azure,
        )

        # Encode original image
        _, buffer = cv2.imencode(".png", original_image_bgr)
        original_image_base64 = base64.b64encode(buffer).decode("utf-8")

        processing_time = time.time() - start_time
        track_image_processed(processing_time)

        logger.info(
            f"Prediction (both models) completed successfully in "
            f"{processing_time:.2f} seconds."
        )

        # Prepare Azure message based on success
        azure_message = (
            "Prediction and analysis successful (azure)"
            if azure_prediction_successful
            else "Azure model unavailable - using local model results as fallback"
        )

        return {
            "local": {
                "message": "Prediction and analysis successful (local)",
                "original_image": original_image_base64,
                "full_size_overlay_image": full_size_overlay_image_base64_local,
                "full_size_mask_image": full_size_mask_image_base64_local,
                "full_size_rois_image": full_size_rois_image_base64_local,
                "full_size_tip_base_image": full_size_tip_base_image_base64_local,
                "root_analysis_results": final_analysis_data_local,
            },
            "azure": {
                "message": azure_message,
                "original_image": original_image_base64,
                "full_size_overlay_image": full_size_overlay_image_base64_azure,
                "full_size_mask_image": full_size_mask_image_base64_azure,
                "full_size_rois_image": full_size_rois_image_base64_azure,
                "full_size_tip_base_image": full_size_tip_base_image_base64_azure,
                "root_analysis_results": final_analysis_data_azure,
            },
        }
    except HTTPException as he:
        logger.warning(f"HTTPException raised: {he.detail}")
        raise he
    except ValueError as ve:
        logger.error(f"Client value error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    # E722 do not use bare 'except' - Replaced with specific exception or
    # a general Exception with detailed traceback logging.
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Unexpected error during prediction (both models):\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during prediction (both models): {str(e)}",
        )


class DeploymentName(str, Enum):
    blue = "blue"
    green = "green"


class LogRequest(BaseModel):
    deployment_name: DeploymentName
    lines: int = Field(200, gt=0, le=1000)


@router.post("/get-logs")
def get_deployment_logs(request: LogRequest):
    try:
        # Load credentials from environment variables only
        tenant_id = os.getenv("AZURE_TENANT_ID")
        service_principal_id = os.getenv("AZURE_CLIENT_ID")
        service_principal_password = os.getenv("AZURE_CLIENT_SECRET")
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
        online_endpoint_name = "root-mask-predictor"

        if not all(
            [
                tenant_id,
                service_principal_id,
                service_principal_password,
                subscription_id,
                resource_group,
                workspace_name,
            ]
        ):
            raise HTTPException(
                status_code=500,
                detail="One or more Azure environment variables are not set.",
            )

        credential = ClientSecretCredential(
            tenant_id, service_principal_id, service_principal_password
        )
        ml_client = MLClient(
            credential, subscription_id, resource_group, workspace_name
        )

        logs = ml_client.online_deployments.get_logs(
            name=request.deployment_name.value,
            endpoint_name=online_endpoint_name,
            lines=request.lines,
        )
        logs_content = logs.decode("utf-8") if isinstance(logs, bytes) else str(logs)
        return {"logs": logs_content}
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Deployment '{request.deployment_name}' not found."
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")


@router.post("/set-routing")
def set_routing(blue_percent: int = Body(...), green_percent: int = Body(...)):
    if not (
        0 <= blue_percent <= 100
        and 0 <= green_percent <= 100
        and blue_percent + green_percent == 100
    ):
        raise HTTPException(
            status_code=400,
            detail="Percentages must be between 0 and 100 and sum to 100.",
        )
    # Authenticate with Azure ML
    ml_client = MLClient(
        DefaultAzureCredential(),
        os.environ["AZURE_SUBSCRIPTION_ID"],
        os.environ["AZURE_RESOURCE_GROUP"],
        os.environ["AZURE_WORKSPACE_NAME"],
    )
    endpoint_name = os.environ["AZURE_ONLINE_ENDPOINT_NAME"]
    try:
        shift_traffic(ml_client, endpoint_name, blue_percent, green_percent)
    except Exception as e:
        logger.exception(f"Failed to shift traffic in Azure: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to shift traffic in Azure: {e}"
        )
    current_routing["blue_percent"] = blue_percent
    current_routing["green_percent"] = green_percent
    return {"message": "Routing updated successfully."}
