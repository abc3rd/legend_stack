"""
Transcriber API Routes - FastAPI endpoints for text-to-JSON conversion
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from transcriber_service import TranscriberService
import os

router = APIRouter(prefix="/api/transcriber", tags=["transcriber"])


# Request/Response Models
class TranscribeRequest(BaseModel):
    text: str = Field(..., description="The text to convert to AI format", min_length=1)
    provider: str = Field(default="generic", description="AI provider (openai, anthropic, ollama, google, cohere, huggingface, generic)")
    model: Optional[str] = Field(default=None, description="Model name (provider-specific)")
    system_message: Optional[str] = Field(default=None, description="System message/prompt")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Temperature (0.0-2.0)")
    max_tokens: Optional[int] = Field(default=None, gt=0, description="Maximum tokens")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional provider-specific parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Explain quantum computing in simple terms",
                "provider": "openai",
                "model": "gpt-4",
                "system_message": "You are a helpful physics teacher",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }


class BatchTranscribeRequest(BaseModel):
    text: str = Field(..., description="The text to convert", min_length=1)
    providers: List[str] = Field(..., description="List of AI providers", min_items=1)
    model: Optional[str] = Field(default=None, description="Model name (applied to all)")
    system_message: Optional[str] = Field(default=None, description="System message (applied to all)")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)


class TranscribeResponse(BaseModel):
    provider: str
    payload: Dict[str, Any]
    formatted_json: str


# API Endpoints
@router.get("/", response_class=HTMLResponse)
async def get_transcriber_ui():
    """Serve the transcriber web interface"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "transcriber.html")

    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        # Return a simple inline version if file doesn't exist
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Transcriber</title></head>
        <body>
            <h1>Transcriber API</h1>
            <p>Use /api/transcriber/docs for API documentation</p>
            <p>Web UI not found. Please access /docs for interactive API testing.</p>
        </body>
        </html>
        """)


@router.get("/providers")
async def get_providers():
    """Get list of supported AI providers"""
    return {
        "providers": TranscriberService.get_supported_providers(),
        "count": len(TranscriberService.SUPPORTED_PROVIDERS)
    }


@router.post("/convert", response_model=TranscribeResponse)
async def convert_text(request: TranscribeRequest):
    """
    Convert text to AI provider JSON format

    This endpoint takes plain text and converts it into the appropriate
    JSON payload format for the specified AI provider.
    """
    try:
        # Build kwargs based on what's provided
        kwargs = {}

        if request.model:
            kwargs["model"] = request.model
        if request.system_message:
            kwargs["system_message"] = request.system_message
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.additional_params:
            kwargs["additional_params"] = request.additional_params

        # Convert the text
        payload = TranscriberService.convert(
            text=request.text,
            provider=request.provider,
            **kwargs
        )

        # Format JSON for display
        formatted_json = TranscriberService.format_json(payload)

        return TranscribeResponse(
            provider=request.provider,
            payload=payload,
            formatted_json=formatted_json
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/convert/batch")
async def convert_text_batch(request: BatchTranscribeRequest):
    """
    Convert text to multiple AI provider formats at once

    Useful for comparing different provider payload structures
    or preparing multi-provider integrations.
    """
    try:
        # Build kwargs
        kwargs = {}
        if request.model:
            kwargs["model"] = request.model
        if request.system_message:
            kwargs["system_message"] = request.system_message
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        # Convert for all providers
        results = TranscriberService.convert_batch(
            text=request.text,
            providers=request.providers,
            **kwargs
        )

        # Format the results
        formatted_results = {}
        for provider, payload in results.items():
            formatted_results[provider] = {
                "payload": payload,
                "formatted_json": TranscriberService.format_json(payload)
            }

        return {
            "text": request.text,
            "providers": request.providers,
            "results": formatted_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")


@router.get("/convert/quick")
async def quick_convert(
    text: str = Query(..., description="Text to convert", min_length=1),
    provider: str = Query(default="generic", description="AI provider"),
    model: Optional[str] = Query(default=None, description="Model name"),
):
    """
    Quick conversion endpoint using query parameters

    Useful for simple GET requests and quick testing
    """
    try:
        kwargs = {}
        if model:
            kwargs["model"] = model

        payload = TranscriberService.convert(
            text=text,
            provider=provider,
            **kwargs
        )

        return JSONResponse(content=payload)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.get("/examples/{provider}")
async def get_provider_example(provider: str):
    """
    Get example payload for a specific provider

    Returns a sample conversion to help users understand the output format
    """
    example_text = "Hello! How can I help you today?"

    try:
        payload = TranscriberService.convert(
            text=example_text,
            provider=provider
        )

        return {
            "provider": provider,
            "example_input": example_text,
            "example_output": payload,
            "formatted_json": TranscriberService.format_json(payload)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate example: {str(e)}")
