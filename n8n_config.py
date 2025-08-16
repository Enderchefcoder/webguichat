"""
n8n Webhook Configuration for Open WebUI

This file contains the configuration settings for integrating Open WebUI with n8n webhooks.
Update the values below with your actual n8n webhook details.
"""

import os

# n8n Webhook Configuration
# Replace with your actual n8n webhook URL
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "YOUR_N8N_WEBHOOK_URL")

# Optional: Add authentication token if your n8n webhook requires authentication
N8N_WEBHOOK_AUTH_TOKEN = os.getenv("N8N_WEBHOOK_AUTH_TOKEN", "")

# Model Configuration
N8N_MODEL_NAME = os.getenv("N8N_MODEL_NAME", "n8n-agent")
N8N_MODEL_DESCRIPTION = os.getenv("N8N_MODEL_DESCRIPTION", "n8n Webhook Agent for AI interactions")

# Request Configuration
N8N_TIMEOUT = int(os.getenv("N8N_TIMEOUT", "120"))  # Timeout in seconds
N8N_MAX_RETRIES = int(os.getenv("N8N_MAX_RETRIES", "3"))  # Maximum number of retries

# Default Model Parameters
N8N_DEFAULT_TEMPERATURE = float(os.getenv("N8N_DEFAULT_TEMPERATURE", "0.7"))
N8N_DEFAULT_MAX_TOKENS = int(os.getenv("N8N_DEFAULT_MAX_TOKENS", "2048"))
N8N_DEFAULT_TOP_P = float(os.getenv("N8N_DEFAULT_TOP_P", "1.0"))

# Debug Mode
N8N_DEBUG = os.getenv("N8N_DEBUG", "false").lower() == "true"

# Instructions for setup:
"""
1. Create an n8n workflow with a Webhook node as the trigger
2. Configure the webhook to accept POST requests
3. Add nodes to process the incoming chat messages
4. Return a JSON response with the AI-generated content
5. Copy the webhook URL from n8n
6. Update N8N_WEBHOOK_URL above or set the N8N_WEBHOOK_URL environment variable
7. Optionally, add authentication if needed

Example n8n workflow response format:
{
    "content": "Your AI response here",
    "model": "n8n-agent",
    "finish_reason": "stop"
}

For streaming responses, your n8n workflow should return Server-Sent Events (SSE) format:
data: {"content": "chunk1", "finish_reason": null}
data: {"content": "chunk2", "finish_reason": null}
data: {"content": "", "finish_reason": "stop"}
data: [DONE]
"""