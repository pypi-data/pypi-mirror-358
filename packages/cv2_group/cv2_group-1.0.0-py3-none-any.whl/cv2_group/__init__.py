"""
Package
"""

# Here we import everything for easy access
# Should allow for "from cv2_group import crop_image"
# OR import cv2_group (to use: cv2_group.crop_image())
# Make sure this list stays up to date with new functions
from cv2_group.data.data_ingestion import (
    load_image,
    upload_data,
    rename_pairs,
    upload_to_azure_datastore,
)
from cv2_group.data.data_processing import (
    crop_image,
    crop_image_with_bbox,
    pad_image,
    pad_image_alternative,
    create_patches,
    create_patches_alternative,
    unpatch_image,
    remove_padding,
    uncrop_mask,
)
from cv2_group.data.data_validation import is_binary_mask, check_size_match
from cv2_group.features.feature_extraction import (
    process_predicted_mask,
    find_labels_in_rois,
    extract_root_instances,
    analyze_primary_root,
)
from cv2_group.models.model_definitions import load_trained_model
from cv2_group.models.model_evaluation import (
    print_best_val_metrics,
    plot_loss,
    plot_f1,
    load_images_and_masks,
    pixel_accuracy,
    iou_score,
    evaluate_model_on_data,
    load_test,
    evaluate_local_model_on_data,
    evaluate_model_on_data_with_model,
)
from cv2_group.models.model_saving import save_model
from cv2_group.models.model_training import (
    load_and_prepare_model_for_retraining,
    load_image_mask_arrays,
    create_data_generators,
    train_unet_model
)
from cv2_group.utils.api_models import SaveImageRequest
from cv2_group.utils.azure_blob import (
    get_container_client,
    upload_blob,
    download_blob,
    blob_exists,
    list_blobs_in_folder,
    delete_blob,
    get_blob_url,
)
from cv2_group.utils.azure_integration import (
    initialize_azure_workspace,
    get_azure_workspace,
    get_azure_datastore,
    is_azure_available,
)
from cv2_group.utils.azure_model_loader import load_model_from_azure_registry
from cv2_group.utils.binary import ensure_binary_mask
from cv2_group.utils.dashboard_stats import (
    get_dashboard_stats,
    track_download,
    track_image_processed,
    track_mask_reanalyzed,
    reset_dashboard_stats,
)
from cv2_group.utils.feedback_system import (
    FeedbackImageData,
    FeedbackAnalysisData,
    FeedbackSubmission,
    FeedbackEntry,
    get_blob_client,
    get_blob_url,
    load_feedback_data,
    save_feedback_data,
    save_base64_image_to_blob,
    add_feedback_entry,
    get_feedback_entries,
    get_feedback_entries_for_image,
    delete_feedback_entry,
    initialize_feedback_storage
)
from cv2_group.utils.helpers import (
    _transform_rois_to_cropped_coords,
    recall,
    precision,
    f1,
    numpy_to_base64_png,
    _transform_rois_to_cropped_coords,
    shift_traffic,
    encode_mask_for_json,
    unpack_model_response,
    numpy_to_base64_png,
)
from cv2_group.utils.image_helpers import (
    _transform_analysis_results_for_cropped_view,
    unpack_model_response,
    decode_b64_png_to_ndarray,
)
from cv2_group.utils.image_processing import _process_input_image, _process_rois_json

# New utility modules
from cv2_group.utils.llama_service import LlamaRequest, LlamaResponse, LlamaService

from cv2_group.utils.predicting import (
    predict_root,
    _prepare_image_for_model,
    _reconstruct_and_uncrop_mask,
    predict_from_array,
)
from cv2_group.utils.visualization import (
    _draw_rois_on_image,
    _overlay_mask_on_image,
    _draw_tip_base_and_path,
    _image_to_base64,
    _generate_full_size_visualizations,
    create_side_by_side_visualization,
    draw_all_root_skeletons_on_image,
)

__all__ = [

    # Data ingestion
    "load_image",
    "upload_data",
    "rename_pairs",
    "upload_to_azure_datastore",

    # Data processing
    "crop_image",
    "crop_image_with_bbox",
    "pad_image",
    "pad_image_alternative",
    "create_patches",
    "create_patches_alternative",
    "unpatch_image",
    "remove_padding",
    "uncrop_mask",

    # Data validation
    "is_binary_mask",
    "check_size_match",

    # Feature extraction
    "process_predicted_mask",
    "find_labels_in_rois",
    "extract_root_instances",
    "analyze_primary_root",

    # Model definitions
    "load_trained_model",

    # Model evaluation
    "print_best_val_metrics",
    "plot_loss",
    "plot_f1",
    "load_images_and_masks",
    "pixel_accuracy",
    "iou_score",
    "evaluate_model_on_data",
    "load_test",
    "evaluate_local_model_on_data",
    "evaluate_model_on_data_with_model",

    # Model saving
    "save_model",

    # Model training
    "load_and_prepare_model_for_retraining",
    "load_image_mask_arrays",
    "create_data_generators",
    "train_unet_model",

    # API Models
    "SaveImageRequest",

    # Azure Blob Utils
    "get_container_client",
    "upload_blob",
    "download_blob",
    "blob_exists",
    "list_blobs_in_folder",
    "delete_blob",
    "get_blob_url",

    # Azure integration
    "initialize_azure_workspace",
    "get_azure_workspace",
    "get_azure_datastore",
    "is_azure_available",

    # Azure model loading
    "load_model_from_azure_registry",

    # Binary mask utilities
    "ensure_binary_mask",

    # Dashboard stats
    "get_dashboard_stats",
    "track_download",
    "track_image_processed",
    "track_mask_reanalyzed",
    "reset_dashboard_stats",

    # Feedback system
    "FeedbackImageData",
    "FeedbackAnalysisData",
    "FeedbackSubmission",
    "FeedbackEntry",
    "get_blob_client",
    "get_blob_url",
    "load_feedback_data",
    "save_feedback_data",
    "save_base64_image_to_blob",
    "add_feedback_entry",
    "get_feedback_entries",
    "get_feedback_entries_for_image",
    "delete_feedback_entry",
    "initialize_feedback_storage",

    # Helpers
    "recall",
    "precision",
    "f1",
    "numpy_to_base64_png",
    "shift_traffic",
    "encode_mask_for_json",
    "unpack_model_response",

    # Image helpers
    "decode_b64_png_to_ndarray",

    # LLaMA service
    "LlamaRequest",
    "LlamaResponse",
    "LlamaService",

    # Predicting
    "predict_root",
    "predict_from_array",

    # Visualization
    "create_side_by_side_visualization",
    "draw_all_root_skeletons_on_image",
]
