# n8n Webhook Integration for Open WebUI

This modified version of Open WebUI is configured to work exclusively with n8n webhooks as the AI model provider. All other model providers (Ollama, OpenAI, etc.) have been disabled.

## 🚀 Quick Start

### 1. Set up your n8n workflow

Create an n8n workflow with:

1. **Webhook node** as the trigger (accepts POST requests)
2. **Processing nodes** to handle the chat messages
3. **Response node** that returns the AI-generated content

### 2. Configure Open WebUI

Run the setup script:

```bash
python setup_n8n.py
```

Or manually configure by:

1. Copy `.env.n8n.example` to `.env`
2. Update `N8N_WEBHOOK_URL` with your n8n webhook URL
3. Optionally add authentication token if required

### 3. Start Open WebUI

```bash
# Install dependencies
npm install
pip install -r backend/requirements.txt

# Start the application
npm run dev
```

## 📋 n8n Workflow Requirements

Your n8n workflow should:

### Input Format

The webhook will receive a POST request with:

```json
{
	"model": "n8n-agent",
	"messages": [
		{ "role": "system", "content": "System prompt" },
		{ "role": "user", "content": "User message" }
	],
	"temperature": 0.7,
	"max_tokens": 2048,
	"stream": false,
	"user": {
		"id": "user_id",
		"name": "User Name",
		"email": "user@example.com",
		"role": "user"
	}
}
```

### Output Format

#### Non-streaming Response

Return a JSON object:

```json
{
	"content": "The AI-generated response",
	"model": "n8n-agent",
	"finish_reason": "stop"
}
```

#### Streaming Response (SSE format)

For streaming, return Server-Sent Events:

```
data: {"content": "First chunk", "finish_reason": null}
data: {"content": "Second chunk", "finish_reason": null}
data: {"content": "", "finish_reason": "stop"}
data: [DONE]
```

## 🔧 Configuration Options

### Environment Variables

| Variable                  | Description                     | Default   |
| ------------------------- | ------------------------------- | --------- |
| `N8N_WEBHOOK_URL`         | Your n8n webhook URL            | Required  |
| `N8N_WEBHOOK_AUTH_TOKEN`  | Authentication token (optional) | Empty     |
| `N8N_MODEL_NAME`          | Model name displayed in UI      | n8n-agent |
| `N8N_TIMEOUT`             | Request timeout in seconds      | 120       |
| `N8N_MAX_RETRIES`         | Maximum retry attempts          | 3         |
| `N8N_DEFAULT_TEMPERATURE` | Default temperature (0-1)       | 0.7       |
| `N8N_DEFAULT_MAX_TOKENS`  | Default max response length     | 2048      |
| `N8N_DEBUG`               | Enable debug logging            | false     |

## 🧪 Testing Your Integration

### Using the Setup Script

```bash
python setup_n8n.py
# Follow the prompts and test your webhook
```

### Manual Testing

```bash
curl -X POST "YOUR_N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, test message"}
    ]
  }'
```

## 📝 Example n8n Workflows

### Simple OpenAI Integration

1. Webhook → OpenAI Chat Model → Respond to Webhook

### Advanced Processing

1. Webhook → Code (parse messages) → AI Chain → Format Response → Respond to Webhook

### With Context/RAG

1. Webhook → Vector Store Search → Merge Context → LLM → Respond to Webhook

## 🐛 Troubleshooting

### Webhook Not Responding

- Verify n8n workflow is active
- Check webhook URL is correct
- Ensure n8n instance is accessible from Open WebUI server
- Check firewall/network settings

### Authentication Issues

- Verify auth token matches n8n webhook configuration
- Check token format (Bearer token, API key, etc.)

### Response Format Issues

- Ensure n8n returns proper JSON format
- For streaming, use correct SSE format
- Check Content-Type headers in n8n response

### Debug Mode

Enable debug logging:

```bash
export N8N_DEBUG=true
# or in .env file
N8N_DEBUG=true
```

Then check logs for detailed information.

## 🔄 Reverting Changes

To restore original Open WebUI functionality:

1. Edit `/home/user/webapp/backend/open_webui/main.py`
2. Uncomment the original router includes:
   ```python
   app.include_router(ollama.router, prefix="/ollama", tags=["ollama"])
   app.include_router(openai.router, prefix="/openai", tags=["openai"])
   ```
3. Remove or comment out n8n router includes:
   ```python
   # app.include_router(n8n_webhook.router, prefix="/n8n", tags=["n8n"])
   # app.include_router(n8n_webhook.router, prefix="/openai", tags=["n8n"])
   ```

## 📚 Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Webhook Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Open WebUI Documentation](https://docs.openwebui.com/)

## 💡 Tips

1. **Performance**: For better performance, keep your n8n workflow simple and optimize processing nodes
2. **Error Handling**: Add error handling nodes in n8n to gracefully handle failures
3. **Logging**: Use n8n's built-in logging for debugging workflow issues
4. **Caching**: Consider implementing caching in n8n for frequently requested data
5. **Security**: Always use HTTPS for production webhooks and implement proper authentication

## 🤝 Support

For issues specific to this n8n integration:

1. Check this documentation
2. Enable debug mode and check logs
3. Test your n8n workflow independently
4. Verify network connectivity between Open WebUI and n8n

For general Open WebUI issues, refer to the main documentation.
