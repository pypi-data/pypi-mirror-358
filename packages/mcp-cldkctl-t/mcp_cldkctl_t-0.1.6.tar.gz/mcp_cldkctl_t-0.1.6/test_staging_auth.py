#!/usr/bin/env python3
"""
Test script for cldkctl MCP authentication with staging URL.
"""

import sys
import os
import requests
import base64
import json

def test_staging_auth():
    """Test authentication with staging URL."""
    print("Testing cldkctl authentication with staging URL...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    base_url = "https://staging.ai.cloudeka.id"
    
    print(f"Login token: {sample_token}")
    print(f"Base URL: {base_url}")
    
    # Test the auth endpoint
    url = base_url + "/core/cldkctl/auth"
    payload = {"token": sample_token}
    
    try:
        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        print(f"Response status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            jwt_token = data.get("data", {}).get("token")
            if jwt_token:
                print(f"✅ Success! JWT token obtained: {jwt_token[:50]}...")
                return True
            else:
                print("❌ No JWT token in response")
                return False
        else:
            print(f"❌ Failed with status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_staging_auth()
    sys.exit(0 if success else 1) 