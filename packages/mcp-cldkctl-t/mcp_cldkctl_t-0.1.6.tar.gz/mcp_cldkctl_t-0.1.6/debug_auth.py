#!/usr/bin/env python3
"""
Standalone debug script for cldkctl authentication API.
This script tests the API directly without MCP dependencies.
"""

import requests
import json
import os

def test_exact_go_cli_behavior():
    """Test the exact same request as the Go CLI."""
    print("Testing exact Go CLI behavior...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    base_url = "https://ai.cloudeka.id"
    
    print(f"Login token: {sample_token}")
    print(f"Base URL: {base_url}")
    
    # Test 1: Exact Go CLI behavior (no Authorization header)
    print("\n=== Test 1: Exact Go CLI behavior (no Authorization header) ===")
    url1 = base_url + "/core/cldkctl/auth"
    payload1 = {"token": sample_token}
    
    try:
        # This is exactly what the Go CLI does - no Authorization header
        resp1 = requests.post(url1, json=payload1, headers={'Content-Type': 'application/json'})
        print(f"Status: {resp1.status_code}")
        print(f"Response: {resp1.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With environment variables that Go CLI might use
    print("\n=== Test 2: With DEV environment variables ===")
    # Set environment variables that Go CLI might use
    os.environ['DEV_CAPTCHA_BYPASS'] = 'test_captcha'
    os.environ['DEV_CID_BYPASS'] = 'test_cid'
    
    try:
        resp2 = requests.post(url1, json=payload1, headers={'Content-Type': 'application/json'})
        print(f"Status: {resp2.status_code}")
        print(f"Response: {resp2.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Check if there are any other headers the Go CLI might send
    print("\n=== Test 3: With additional headers ===")
    additional_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'cldkctl/1.0',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    try:
        resp3 = requests.post(url1, json=payload1, headers=additional_headers)
        print(f"Status: {resp3.status_code}")
        print(f"Response: {resp3.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Check if the Go CLI is using a different base URL
    print("\n=== Test 4: Check if Go CLI uses different base URL ===")
    # Let's check what base URL the Go CLI is actually using
    print("Go CLI might be using a different base URL. Check your Go CLI config.")
    print("You can check with: cldkctl config get BASE_URL")

def test_staging_vs_production():
    """Test both staging and production URLs."""
    print("Testing staging vs production URLs...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    
    # Test both URLs
    urls = [
        "https://ai.cloudeka.id",  # Production
        "https://staging.ai.cloudeka.id"  # Staging
    ]
    
    for base_url in urls:
        print(f"\n=== Testing {base_url} ===")
        
        # Test auth endpoint
        url = base_url + "/core/cldkctl/auth"
        payload = {"token": sample_token}
        
        try:
            resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            print(f"Auth endpoint status: {resp.status_code}")
            print(f"Auth endpoint response: {resp.text}")
        except Exception as e:
            print(f"Auth endpoint error: {e}")
        
        # Test token generation endpoint (for comparison)
        token_url = base_url + "/core/cldkctl/token"
        try:
            # This would need a valid JWT, but let's see what error we get
            resp2 = requests.post(token_url, headers={'Authorization': 'Bearer invalid_jwt', 'Content-Type': 'application/json'})
            print(f"Token generation status: {resp2.status_code}")
            print(f"Token generation response: {resp2.text}")
        except Exception as e:
            print(f"Token generation error: {e}")

if __name__ == "__main__":
    test_exact_go_cli_behavior()
    test_staging_vs_production() 