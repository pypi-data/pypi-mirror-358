import os
from typing import Any, Dict, Optional, Tuple

import numpy as np
from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from cv2_group.models.model_evaluation import load_test
from cv2_group.utils.helpers import encode_mask_for_json

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

router = APIRouter()


class LoadTestResult(BaseModel):
    deployment_target: str
    total_requests: int
    success_count: int
    failure_count: int
    unpack_failure_count: int
    average_time_s: float
    max_time_s: float
    min_time_s: float
    success_rate: float
    mask_image_png_base64: Optional[str] = None
    bounding_box: Optional[Tuple] = None


class ComparisonResult(BaseModel):
    blue_deployment: LoadTestResult
    green_deployment: LoadTestResult
    performance_summary: Dict[str, str]
    output_comparison: Dict[str, Any]


@router.post("/test/load-test", response_model=LoadTestResult)
async def run_single_load_test(
    image: UploadFile = File(...),
    deployment_target: str = Form(...),
    num_requests: int = Form(10),
    min_delay: float = Form(0.1),
    max_delay: float = Form(0.5),
):
    api_key = os.getenv("AZURE_ML_API_KEY")
    api_url = os.getenv("AZURE_ML_ENDPOINT_URL")
    print("DEBUG: AZURE_ML_API_KEY =", api_key)
    print("DEBUG: AZURE_ML_ENDPOINT_URL =", api_url)
    if not api_key:
        raise HTTPException(
            status_code=500, detail="Azure ML API Key is not configured on the server."
        )
    image_bytes = await image.read()
    results = await load_test(
        api_url=api_url,
        image_bytes=image_bytes,
        api_key=api_key,
        deployment_target=deployment_target,
        num_requests=num_requests,
        min_delay=min_delay,
        max_delay=max_delay,
    )
    sample_response = results.get("sample_response")
    mask_image_png_base64 = None
    bounding_box = None
    if sample_response:
        mask = sample_response.get("mask")
        mask_image_png_base64 = encode_mask_for_json(mask)
        bounding_box = sample_response.get("bounding_box")
    return LoadTestResult(
        deployment_target=deployment_target,
        total_requests=results["total_requests"],
        success_count=results["success_count"],
        failure_count=results["failure_count"],
        unpack_failure_count=results["unpack_failure_count"],
        average_time_s=results["average_time_s"],
        max_time_s=results["max_time_s"],
        min_time_s=results["min_time_s"],
        success_rate=results["success_rate"],
        mask_image_png_base64=mask_image_png_base64,
        bounding_box=bounding_box,
    )


def sanitize_results(results):
    sanitized = {}
    for k, v in results.items():
        sanitized[k] = v.copy()
        # Remove or replace sample_unpacked_response
        # (or any other non-serializable fields)
        if "error" in sanitized[k]:
            sanitized[k]["error"] = None
        if "sample_unpacked_response" in sanitized[k]:
            sanitized[k]["sample_unpacked_response"] = None
    return sanitized


@router.post("/test/compare-deployments")
async def compare_deployments(
    image: UploadFile = File(...),
    num_requests: int = Form(10),
    min_delay: float = Form(0.1),
    max_delay: float = Form(0.5),
):
    # Read image bytes
    image_bytes = await image.read()
    # Get API URL and key from env
    api_url = os.getenv("AZURE_ML_ENDPOINT_URL")
    api_key = os.getenv("AZURE_ML_API_KEY")
    deployments = ["blue", "green"]
    deployment_results_storage = {}

    for deployment_target in deployments:
        try:
            results = await load_test(
                api_url=api_url,
                image_bytes=image_bytes,
                api_key=api_key,
                deployment_target=deployment_target,
                num_requests=num_requests,
                min_delay=min_delay,
                max_delay=max_delay,
            )
            # Extract mask image and bounding box if possible
            mask_image_png_base64 = None
            bounding_box = None
            sample_response = results.get("sample_unpacked_response")
            if sample_response:
                mask = sample_response[1] if len(sample_response) > 1 else None
                if mask is not None:
                    mask_image_png_base64 = encode_mask_for_json(mask)
                bounding_box = sample_response[2] if len(sample_response) > 2 else None
            results["mask_image_png_base64"] = mask_image_png_base64
            results["bounding_box"] = bounding_box
            deployment_results_storage[deployment_target] = results
        except Exception as e:
            deployment_results_storage[deployment_target] = {
                "deployment_target": deployment_target,
                "success_count": 0,
                "failure_count": num_requests,
                "unpack_failure_count": 0,
                "response_times": [],
                "average_time_s": None,
                "max_time_s": None,
                "min_time_s": None,
                "success_rate": 0,
                "sample_unpacked_response": None,
                "mask_image_png_base64": None,
                "bounding_box": None,
                "error": str(e),
            }

    # Now use robust comparison logic
    summary = {}
    for deploy_name, results in deployment_results_storage.items():
        total_reqs = results.get("success_count", 0) + results.get("failure_count", 0)
        summary[deploy_name] = {
            "total_requests": total_reqs,
            "successful_requests": results["success_count"],
            "failed_requests": results["failure_count"],
            "unpacking_failures": results["unpack_failure_count"],
            "average_response_time": results["average_time_s"],
            "max_response_time": results["max_time_s"],
            "min_response_time": results["min_time_s"],
            "success_rate": results["success_rate"],
            "mask_image_png_base64": results.get("mask_image_png_base64"),
            "bounding_box": results.get("bounding_box"),
        }

    # Optionally, add mask stats, bounding box, etc. as in your function
    deployments_with_samples = {
        name: res["sample_unpacked_response"]
        for name, res in deployment_results_storage.items()
        if res and res["sample_unpacked_response"] is not None
    }
    mask_stats = {}
    for deploy_name, sample_data in deployments_with_samples.items():
        uncropped_mask = sample_data[1]
        if uncropped_mask is not None:
            mask_stats[deploy_name] = {
                "mask_shape": uncropped_mask.shape,
                "mask_dtype": str(uncropped_mask.dtype),
                "mask_unique_values": np.unique(uncropped_mask).tolist(),
                "mask_sum": int(np.sum(uncropped_mask > 0)),
                "original_bbox": sample_data[2],
                "square_offsets": sample_data[3],
            }
        else:
            mask_stats[deploy_name] = None

    return {
        "summary": summary,
        "mask_stats": mask_stats,
        "raw_results": sanitize_results(deployment_results_storage),
    }
