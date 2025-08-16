#!/usr/bin/env python3
"""
Setup script for n8n Webhook Integration with Open WebUI

This script helps configure and test the n8n webhook integration.
"""

import os
import sys
import json
import requests
from urllib.parse import urlparse

def validate_webhook_url(url):
    """Validate if the provided URL is a valid webhook URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def test_webhook(url, auth_token=None):
    """Test the n8n webhook with a simple request"""
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    test_payload = {
        "model": "n8n-agent",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, this is a test message. Please respond with 'Test successful!'"}
        ],
        "stream": False
    }
    
    try:
        print(f"Testing webhook at: {url}")
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhook responded successfully!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            except:
                print(f"Response (text): {response.text}")
                return True
        else:
            print(f"❌ Webhook returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Webhook request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook")
        return False
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

def setup_n8n():
    """Interactive setup for n8n webhook integration"""
    print("=" * 60)
    print("n8n Webhook Integration Setup for Open WebUI")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    env_file = ".env"
    env_exists = os.path.exists(env_file)
    
    if env_exists:
        print(f"Found existing {env_file}")
        overwrite = input("Do you want to update n8n configuration? (y/n): ").lower() == 'y'
        if not overwrite:
            print("Setup cancelled.")
            return
    
    # Get webhook URL
    print("\nStep 1: n8n Webhook URL")
    print("-" * 40)
    print("Enter your n8n webhook URL (from the Webhook node in your n8n workflow)")
    webhook_url = input("Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ Webhook URL is required!")
        return
    
    if not validate_webhook_url(webhook_url):
        print("❌ Invalid webhook URL format!")
        return
    
    # Get authentication token (optional)
    print("\nStep 2: Authentication (Optional)")
    print("-" * 40)
    print("If your n8n webhook requires authentication, enter the token.")
    print("Press Enter to skip if not required.")
    auth_token = input("Auth Token (optional): ").strip()
    
    # Test the webhook
    print("\nStep 3: Test Connection")
    print("-" * 40)
    test = input("Do you want to test the webhook now? (y/n): ").lower() == 'y'
    
    if test:
        success = test_webhook(webhook_url, auth_token if auth_token else None)
        if not success:
            cont = input("\nWebhook test failed. Continue with setup anyway? (y/n): ").lower() == 'y'
            if not cont:
                print("Setup cancelled.")
                return
    
    # Advanced settings
    print("\nStep 4: Advanced Settings (Optional)")
    print("-" * 40)
    use_defaults = input("Use default settings? (y/n): ").lower() == 'y'
    
    if use_defaults:
        model_name = "n8n-agent"
        timeout = "120"
        max_retries = "3"
        temperature = "0.7"
        max_tokens = "2048"
        debug = "false"
    else:
        model_name = input("Model name (default: n8n-agent): ").strip() or "n8n-agent"
        timeout = input("Timeout in seconds (default: 120): ").strip() or "120"
        max_retries = input("Max retries (default: 3): ").strip() or "3"
        temperature = input("Temperature (default: 0.7): ").strip() or "0.7"
        max_tokens = input("Max tokens (default: 2048): ").strip() or "2048"
        debug = input("Enable debug mode? (y/n): ").lower() == 'y'
        debug = "true" if debug else "false"
    
    # Write configuration
    print("\nStep 5: Save Configuration")
    print("-" * 40)
    
    # Read existing .env if it exists
    env_lines = []
    if env_exists:
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add n8n configuration
    n8n_config = {
        "N8N_WEBHOOK_URL": webhook_url,
        "N8N_WEBHOOK_AUTH_TOKEN": auth_token,
        "N8N_MODEL_NAME": model_name,
        "N8N_TIMEOUT": timeout,
        "N8N_MAX_RETRIES": max_retries,
        "N8N_DEFAULT_TEMPERATURE": temperature,
        "N8N_DEFAULT_MAX_TOKENS": max_tokens,
        "N8N_DEBUG": debug
    }
    
    # Remove existing n8n config lines
    env_lines = [line for line in env_lines if not line.strip().startswith("N8N_")]
    
    # Add new n8n configuration
    env_lines.append("\n# n8n Webhook Configuration\n")
    for key, value in n8n_config.items():
        if value:  # Only add non-empty values
            env_lines.append(f"{key}={value}\n")
    
    # Write updated configuration
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Configuration saved to {env_file}")
    
    # Update n8n_config.py
    config_py = "n8n_config.py"
    with open(config_py, 'w') as f:
        f.write(f'''"""
n8n Webhook Configuration for Open WebUI
Auto-generated by setup_n8n.py
"""

import os

# n8n Webhook Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "{webhook_url}")
N8N_WEBHOOK_AUTH_TOKEN = os.getenv("N8N_WEBHOOK_AUTH_TOKEN", "{auth_token}")
N8N_MODEL_NAME = os.getenv("N8N_MODEL_NAME", "{model_name}")
N8N_MODEL_DESCRIPTION = os.getenv("N8N_MODEL_DESCRIPTION", "n8n Webhook Agent for AI interactions")
N8N_TIMEOUT = int(os.getenv("N8N_TIMEOUT", "{timeout}"))
N8N_MAX_RETRIES = int(os.getenv("N8N_MAX_RETRIES", "{max_retries}"))
N8N_DEFAULT_TEMPERATURE = float(os.getenv("N8N_DEFAULT_TEMPERATURE", "{temperature}"))
N8N_DEFAULT_MAX_TOKENS = int(os.getenv("N8N_DEFAULT_MAX_TOKENS", "{max_tokens}"))
N8N_DEFAULT_TOP_P = float(os.getenv("N8N_DEFAULT_TOP_P", "1.0"))
N8N_DEBUG = os.getenv("N8N_DEBUG", "{debug}").lower() == "true"
''')
    
    print(f"✅ Configuration saved to {config_py}")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ensure your n8n workflow is active and properly configured")
    print("2. Restart Open WebUI to apply the changes")
    print("3. The n8n agent will be available as the only model in Open WebUI")
    print("\nFor troubleshooting, check the logs or enable debug mode.")

if __name__ == "__main__":
    try:
        setup_n8n()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup error: {str(e)}")
        sys.exit(1)