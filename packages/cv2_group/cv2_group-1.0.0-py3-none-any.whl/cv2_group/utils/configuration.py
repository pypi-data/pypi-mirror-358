import os

# Constants
PATCH_SIZE = 128
DEFAULT_ROIS = [
    (1035, 400, 250, 500),
    (1530, 400, 250, 500),
    (2005, 400, 250, 500),
    (2480, 400, 250, 500),
    (2955, 400, 250, 500),
]

# Get the absolute path to the directory containing this configuration.py file
# This will be: .../cv2_group_package/src/cv2_group/utils
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate from _current_dir to the 'cv2_group_package' root
# From: .../cv2_group_package/src/cv2_group/utils
# Go up 1 level (os.pardir): .../cv2_group_package/src/cv2_group/
# Go up 2 levels (os.pardir, os.pardir): .../cv2_group_package/src/
# Go up 3 levels (os.pardir, os.pardir, os.pardir): .../cv2_group_package/
_package_root = os.path.abspath(
    os.path.join(
        _current_dir,
        os.pardir,  # up from 'utils' to 'cv2_group'
        os.pardir,  # up from 'cv2_group' to 'src'
        os.pardir,  # up from 'src' to 'cv2_group_package'
    )
)

# Local model path removed. Model will now be loaded from Azure Model Registry.
#
# Required environment variables (set these in your environment, not here!):
#   AZURE_SUBSCRIPTION_ID
#   AZURE_RESOURCE_GROUP
#   AZURE_WORKSPACE_NAME
#   AZURE_TENANT_ID
#   AZURE_CLIENT_ID
#   AZURE_CLIENT_SECRET
#   AZURE_MODEL_NAME
#   AZURE_MODEL_LABEL (optional, defaults to 'latest')
#
# Example usage:
#   from cv2_group.utils.azure_model_loader import load_model_from_azure_registry
#   model = load_model_from_azure_registry()
#
