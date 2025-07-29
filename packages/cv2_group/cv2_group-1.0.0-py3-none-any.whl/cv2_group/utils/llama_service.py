import logging
import os
from typing import Dict, Optional

import requests
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_MAX_TOKENS = int(os.getenv("LLAMA_MAX_TOKENS", 500))


class LlamaRequest(BaseModel):
    """Model for Llama API request."""

    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7


class LlamaResponse(BaseModel):
    """Model for Llama API response."""

    response: str
    error: Optional[str] = None


class LlamaService:
    """Service class for interacting with Llama model."""

    def __init__(self):
        self.base_url = os.getenv("LLAMA_MODEL_ENDPOINT", "http://localhost:11434")
        self.api_key = os.getenv("LLAMA_MODEL_API_KEY", "")
        self.model = os.getenv("LLAMA_MODEL_NAME", "llama3.1:8b-instruct-q8_0")
        self.default_system_prompt = (
            "You are an AI assistant specifically for the Arabidopsis thaliana root "
            "analysis project developed by the Breda University of Applied Sciences "
            "team.\n\n"
            "PROJECT TEAM:\n"
            "- Martin Simons\n"
            "- Yorbe Heeren\n"
            "- Victor Oorthuis\n"
            "- Teun van der Wolf\n"
            "- Arnout Opfergelt\n\n"
            "This project was developed in collaboration with NPEC (Netherlands Plant "
            "Eco-phenotyping Centre).\n\n"
            "YOUR ROLE:\n"
            "- You are an expert in plant science and root phenotyping\n"
            "- You ONLY discuss this specific project and its functionalities\n"
            "- You NEVER claim to be a general AI or language model\n"
            "- You ALWAYS refer to the specific team members and NPEC\n"
            "- You provide clear, accurate information about root systems\n\n"
            "PROJECT CAPABILITIES:\n"
            "1. Image Processing: Process up to 16 images\n"
            "2. Interactive Editing: Adjust ROIs and edit masks\n"
            "3. Reanalysis: Re-evaluate after modifications\n"
            "4. Data Export: Download CSV files with ROI data\n"
            "5. Image Export: Download individual or all images\n"
            "6. Model Training: Upload new image/mask pairs\n\n"
            "IMPORTANT:\n"
            "- When users ask about 'the project', they mean THIS specific project\n"
            "- When users mention 'images', they refer to processed images\n"
            "- NEVER discuss your own architecture or capabilities\n"
            "- ALWAYS maintain focus on root analysis and plant science\n\n"
            "Remember: You are the AI assistant for THIS SPECIFIC PROJECT. "
            "You are not a general AI assistant."
        )

    def set_system_prompt(self, prompt: str) -> None:
        """Update the default system prompt."""
        self.default_system_prompt = prompt

    def _make_api_call(self, request_data: Dict) -> Dict:
        """Make API call to Llama model (unused for chat generation)."""
        try:
            response = requests.post(
                f"{self.base_url}/generate",  # For completions, not chat
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API call to Llama: {str(e)}")
            raise

    def generate_response(self, request: LlamaRequest) -> LlamaResponse:
        """Generate a response using the Llama model via Open Web UI API."""
        url = f"{self.base_url}/api/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Construct messages array for chat completion
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        elif self.default_system_prompt:
            messages.append({"role": "system", "content": self.default_system_prompt})

        messages.append({"role": "user", "content": request.prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": DEFAULT_MAX_TOKENS,
            },
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()

            # The response format may differ; try to extract the message content
            # Try OpenAI-style: result['choices'][0]['message']['content']
            response_text = None
            if "choices" in result and result["choices"]:
                message = result["choices"][0].get("message", {})
                response_text = message.get("content", "")
            elif "message" in result and "content" in result["message"]:
                response_text = result["message"]["content"]

            if not response_text:
                error_msg = f"Invalid or empty response from Llama API: {result}"
                logger.error(error_msg)
                return LlamaResponse(response="", error=error_msg)

            return LlamaResponse(response=response_text)

        except requests.exceptions.Timeout:
            error_msg = (
                "Request timed out after 120 seconds. "
                "The model might be taking too long to generate a response."
            )
            logger.error(error_msg)
            return LlamaResponse(response="", error=error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = (
                "Could not connect to Llama server. Please make sure it is running "
                "and accessible at the specified base_url."
            )
            logger.error(error_msg)
            return LlamaResponse(response="", error=error_msg)
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return LlamaResponse(response="", error=error_msg)
