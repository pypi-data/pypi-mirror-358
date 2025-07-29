import logging
import os
from typing import Optional

from azureml.core import Datastore, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication

logger = logging.getLogger(__name__)

# Global Azure ML objects
ws: Optional[Workspace] = None
datastore: Optional[Datastore] = None


def initialize_azure_workspace() -> bool:
    """
    Initialize Azure ML Workspace connection using Service Principal credentials.

    This function attempts to authenticate to the Azure ML Workspace using service
    principal credentials provided via environment variables. It sets up global
    variables for the workspace and its default datastore upon successful connection.

    Returns:
        bool: True if the workspace and datastore are successfully initialized,
            False otherwise.
    """
    global ws, datastore

    # Get environment variables
    tenant_id = os.getenv("AZURE_TENANT_ID")
    service_principal_id = os.getenv("AZURE_CLIENT_ID")
    service_principal_password = os.getenv("AZURE_CLIENT_SECRET")
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE_NAME")

    try:
        if not all([tenant_id, service_principal_id, service_principal_password]):
            logger.warning(
                "Azure Service Principal environment variables not fully set. "
                "Upload functionality may not work without proper authentication. "
                "Please set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET."
            )
            return False

        logger.info(
            "Attempting to connect to Azure ML Workspace using Service Principal."
        )

        auth = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=service_principal_id,
            service_principal_password=service_principal_password,
        )

        ws = Workspace(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name,
            auth=auth,
        )

        logger.info(f"Successfully connected to Azure ML Workspace: {ws.name}")
        datastore = ws.get_default_datastore()
        logger.info(f"Default datastore obtained: {datastore.name}")
        return True

    except Exception as e:
        logger.error(f"Failed to connect to Azure ML Workspace: {e}", exc_info=True)
        return False


def get_azure_workspace() -> Optional[Workspace]:
    """
    Retrieve the currently initialized Azure ML Workspace instance.

    Returns:
        Optional[Workspace]: The Azure ML Workspace object if initialized, else None.
    """
    return ws


def get_azure_datastore() -> Optional[Datastore]:
    """
    Retrieve the currently initialized Azure ML Datastore instance.

    Returns:
        Optional[Datastore]: The default Azure ML Datastore object
        if initialized, else None.
    """
    return datastore


def is_azure_available() -> bool:
    """
    Check if Azure ML Workspace and Datastore are available and properly configured.

    Returns:
        bool: True if both workspace and datastore are initialized, False otherwise.
    """
    return ws is not None and datastore is not None
