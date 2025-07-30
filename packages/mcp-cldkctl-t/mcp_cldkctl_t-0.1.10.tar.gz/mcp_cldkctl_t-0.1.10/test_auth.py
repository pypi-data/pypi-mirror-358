#!/usr/bin/env python3
"""
Test script for cldkctl MCP authentication flow.
This script tests the token exchange logic without running the full MCP server.
"""

import sys
import os
import requests
import base64
import json

# Add the mcp_cldkctl directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_cldkctl'))

from server import exchange_login_token_for_jwt, TokenCache

def debug_auth_flow():
    """Debug the authentication flow with detailed request/response logging."""
    print("Debugging cldkctl authentication flow...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    base_url = "https://ai.cloudeka.id"
    
    print(f"Login token: {sample_token}")
    print(f"Base URL: {base_url}")
    
    # Prepare the request
    url = base_url + "/core/cldkctl/auth"
    payload = {"token": sample_token}
    
    print(f"Request URL: {url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print(f"Request headers: {{'Content-Type': 'application/json'}}")
    
    try:
        # Make the request
        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        print(f"Response status: {resp.status_code}")
        print(f"Response headers: {dict(resp.headers)}")
        
        if resp.status_code != 200:
            print(f"Error response body: {resp.text}")
            
            # Try to parse as JSON
            try:
                error_data = resp.json()
                print(f"Error response JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("Error response is not JSON")
        else:
            print(f"Success response body: {resp.text}")
            
            # Try to parse as JSON
            try:
                success_data = resp.json()
                print(f"Success response JSON: {json.dumps(success_data, indent=2)}")
            except:
                print("Success response is not JSON")
                
    except Exception as e:
        print(f"Request failed with exception: {e}")

if __name__ == "__main__":
    debug_auth_flow() 