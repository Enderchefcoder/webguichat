"""
n8n Webhook Integration Router for Open WebUI
This router handles communication with an n8n webhook for AI model interactions.
"""

import json
import logging
import time
import uuid
from typing import Optional, AsyncGenerator, Dict, Any

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS
from open_webui.utils.auth import get_verified_user
from open_webui.models.users import UserModel

# Import n8n configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
try:
    from n8n_config import (
        N8N_WEBHOOK_URL,
        N8N_WEBHOOK_AUTH_TOKEN,
        N8N_MODEL_NAME,
        N8N_MODEL_DESCRIPTION,
        N8N_TIMEOUT,
        N8N_MAX_RETRIES,
        N8N_DEFAULT_TEMPERATURE,
        N8N_DEFAULT_MAX_TOKENS,
        N8N_DEFAULT_TOP_P,
        N8N_DEBUG
    )
except ImportError:
    # Fallback to defaults if config file not found
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "YOUR_N8N_WEBHOOK_URL")
    N8N_WEBHOOK_AUTH_TOKEN = os.getenv("N8N_WEBHOOK_AUTH_TOKEN", "")
    N8N_MODEL_NAME = "n8n-agent"
    N8N_MODEL_DESCRIPTION = "n8n Webhook Agent for AI interactions"
    N8N_TIMEOUT = 120
    N8N_MAX_RETRIES = 3
    N8N_DEFAULT_TEMPERATURE = 0.7
    N8N_DEFAULT_MAX_TOKENS = 2048
    N8N_DEFAULT_TOP_P = 1.0
    N8N_DEBUG = False

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG if N8N_DEBUG else SRC_LOG_LEVELS.get("N8N_WEBHOOK", "INFO"))

router = APIRouter()


class N8NChatCompletionRequest(BaseModel):
    """Request model for chat completion via n8n webhook"""
    model: str = N8N_MODEL_NAME
    messages: list[dict]
    stream: bool = False
    temperature: Optional[float] = N8N_DEFAULT_TEMPERATURE
    max_tokens: Optional[int] = N8N_DEFAULT_MAX_TOKENS
    top_p: Optional[float] = N8N_DEFAULT_TOP_P
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    user: Optional[str] = None


async def stream_n8n_response(
    webhook_url: str,
    request_data: dict,
    auth_token: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Stream response from n8n webhook
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    timeout = aiohttp.ClientTimeout(total=N8N_TIMEOUT)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                webhook_url,
                headers=headers,
                json=request_data,
                ssl=False
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    log.error(f"n8n webhook error: {response.status} - {error_text}")
                    yield f"data: {json.dumps({'error': f'n8n webhook error: {error_text}'})}\n\n"
                    return
                
                # Handle streaming response
                if request_data.get("stream", False):
                    async for line in response.content:
                        if line:
                            decoded_line = line.decode('utf-8').strip()
                            if decoded_line.startswith("data: "):
                                yield decoded_line + "\n\n"
                            elif decoded_line:
                                # Format as SSE if not already
                                yield f"data: {decoded_line}\n\n"
                else:
                    # Handle non-streaming response
                    result = await response.json()
                    formatted_response = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": request_data.get("model", N8N_MODEL_NAME),
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": result.get("content", result.get("response", str(result)))
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        }
                    }
                    yield f"data: {json.dumps(formatted_response)}\n\n"
                    yield "data: [DONE]\n\n"
                    
    except aiohttp.ClientError as e:
        log.error(f"n8n webhook connection error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Connection error: {str(e)}'})}\n\n"
    except Exception as e:
        log.error(f"n8n webhook unexpected error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"


@router.get("/models")
async def get_models(user=Depends(get_verified_user)):
    """
    Get available n8n models
    """
    return {
        "object": "list",
        "data": [
            {
                "id": N8N_MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "n8n",
                "permission": [],
                "root": N8N_MODEL_NAME,
                "parent": None,
                "name": N8N_MODEL_NAME.replace("-", " ").title(),
                "description": N8N_MODEL_DESCRIPTION
            }
        ]
    }


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    body: N8NChatCompletionRequest,
    user=Depends(get_verified_user)
):
    """
    Handle chat completion requests via n8n webhook
    """
    log.info(f"n8n chat completion request from user: {user.email}")
    
    # Validate webhook URL
    webhook_url = N8N_WEBHOOK_URL
    if not webhook_url or webhook_url == "YOUR_N8N_WEBHOOK_URL":
        raise HTTPException(
            status_code=500,
            detail="n8n webhook URL not configured. Please set the N8N_WEBHOOK_URL."
        )
    
    # Prepare request data for n8n
    n8n_request = {
        "model": body.model,
        "messages": body.messages,
        "stream": body.stream,
        "temperature": body.temperature,
        "max_tokens": body.max_tokens,
        "top_p": body.top_p,
        "frequency_penalty": body.frequency_penalty,
        "presence_penalty": body.presence_penalty,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }
    
    # Return streaming response
    return StreamingResponse(
        stream_n8n_response(
            webhook_url,
            n8n_request,
            N8N_WEBHOOK_AUTH_TOKEN if N8N_WEBHOOK_AUTH_TOKEN != "YOUR_N8N_WEBHOOK_AUTH_TOKEN" else None
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/embeddings")
async def create_embeddings(
    request: Request,
    body: dict,
    user=Depends(get_verified_user)
):
    """
    Handle embedding requests via n8n webhook (if supported)
    """
    log.info(f"n8n embedding request from user: {user.email}")
    
    # For now, return a placeholder response
    # You can implement actual embedding via n8n if needed
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.0] * 1536,  # Placeholder embedding
                "index": 0
            }
        ],
        "model": "n8n-agent",
        "usage": {
            "prompt_tokens": 0,
            "total_tokens": 0
        }
    }


@router.get("/")
async def get_status(user=Depends(get_verified_user)):
    """
    Get n8n webhook integration status
    """
    configured = N8N_WEBHOOK_URL != "YOUR_N8N_WEBHOOK_URL"
    
    return {
        "status": "ready" if configured else "not_configured",
        "configured": configured,
        "model": "n8n-agent",
        "description": "n8n Webhook Integration for Open WebUI"
    }