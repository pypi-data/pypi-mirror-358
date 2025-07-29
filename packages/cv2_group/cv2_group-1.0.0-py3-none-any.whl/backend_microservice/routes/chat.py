import logging

from fastapi import APIRouter, HTTPException, status

from cv2_group.utils.llama_service import LlamaRequest, LlamaResponse, LlamaService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Llama service
llama_service = LlamaService()


@router.post("/llama/chat", response_model=LlamaResponse)
async def chat_with_llama(request: LlamaRequest):
    """
    Endpoint to interact with the Llama model.
    Allows setting custom system prompts and generating responses.
    """
    try:
        logger.info("Received chat request for Llama model")
        response = llama_service.generate_response(request)

        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error from Llama model: {response.error}",
            )

        return response

    except Exception as e:
        logger.error(f"Error in chat_with_llama endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}",
        )
