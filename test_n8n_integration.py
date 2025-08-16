#!/usr/bin/env python3
"""
Test script for n8n Webhook Integration with Open WebUI

This script tests the n8n integration by making requests to the local Open WebUI API.
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8080"  # Adjust if running on different port
API_KEY = ""  # Add your Open WebUI API key if authentication is enabled

def test_models_endpoint():
    """Test the /models endpoint"""
    print("\n🧪 Testing /models endpoint...")
    print("-" * 40)
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.get(f"{BASE_URL}/n8n/models", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Models endpoint working!")
            print(f"Available models: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Models endpoint returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing models endpoint: {str(e)}")
        return False

def test_chat_completion():
    """Test the chat completion endpoint"""
    print("\n🧪 Testing chat completion...")
    print("-" * 40)
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": "n8n-agent",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you confirm this integration is working?"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/n8n/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # Handle streaming response
            if response.headers.get("content-type") == "text/event-stream":
                print("✅ Chat completion endpoint working (streaming response)!")
                print("Response chunks:")
                for line in response.iter_lines():
                    if line:
                        print(f"  {line.decode('utf-8')}")
            else:
                data = response.json()
                print("✅ Chat completion endpoint working!")
                print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Chat completion returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error with chat completion: {str(e)}")
        return False

def test_streaming_chat():
    """Test streaming chat completion"""
    print("\n🧪 Testing streaming chat completion...")
    print("-" * 40)
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": "n8n-agent",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5 slowly."}
        ],
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/n8n/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Streaming endpoint working!")
            print("Stream chunks:")
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        print(f"  {decoded}")
                        if decoded == "data: [DONE]":
                            break
            return True
        else:
            print(f"❌ Streaming returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error with streaming: {str(e)}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print("\n🧪 Testing status endpoint...")
    print("-" * 40)
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.get(f"{BASE_URL}/n8n/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint working!")
            print(f"Status: {json.dumps(data, indent=2)}")
            
            if data.get("configured"):
                print("✅ n8n webhook is configured!")
            else:
                print("⚠️  n8n webhook URL needs to be configured")
            return True
        else:
            print(f"❌ Status endpoint returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing status endpoint: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("n8n Integration Test Suite")
    print("=" * 60)
    print(f"Testing server at: {BASE_URL}")
    
    if API_KEY:
        print("Using API authentication")
    else:
        print("No API key provided (assuming open access)")
    
    # Run tests
    tests = [
        ("Status Check", test_status_endpoint),
        ("Models Listing", test_models_endpoint),
        ("Chat Completion", test_chat_completion),
        ("Streaming Chat", test_streaming_chat),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test '{name}' failed with error: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The n8n integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        sys.exit(1)