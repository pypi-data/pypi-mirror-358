#!/usr/bin/env python3
"""
Test the /api/cldkctl/auth endpoint.
"""

import requests
import json

def test_api_endpoint():
    """Test the /api/cldkctl/auth endpoint."""
    print("Testing /api/cldkctl/auth endpoint...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    production_url = "https://ai.cloudeka.id"
    
    print(f"Login token: {sample_token}")
    print(f"Production URL: {production_url}")
    
    # Test the api auth endpoint
    url = production_url + "/api/cldkctl/auth"
    payload = {"token": sample_token}
    
    try:
        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        print(f"Response status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
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
            print("❌ Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_api_endpoint() 