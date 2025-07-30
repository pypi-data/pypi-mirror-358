#!/usr/bin/env python3
"""
Test script to check if production URL works with fresh token.
"""

import requests
import json

def test_production_with_fresh_token():
    """Test if production works with a fresh token."""
    print("Testing production URL with fresh token...")
    
    # Test with the real login token
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    production_url = "https://ai.cloudeka.id"
    
    print(f"Login token: {sample_token}")
    print(f"Production URL: {production_url}")
    
    # Test the auth endpoint
    url = production_url + "/core/cldkctl/auth"
    payload = {"token": sample_token}
    
    try:
        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        print(f"Response status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code == 200:
            print("✅ Production URL works!")
            return True
        else:
            print("❌ Production URL still has issues")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_go_cli_behavior():
    """Test to understand how Go CLI might be different."""
    print("\n=== Testing Go CLI behavior simulation ===")
    
    # The Go CLI might be using a different approach
    # Let's test if it's using a different endpoint or method
    
    sample_token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    production_url = "https://ai.cloudeka.id"
    
    # Test 1: Check if there's a different auth endpoint
    endpoints = [
        "/core/cldkctl/auth",
        "/core/user/auth", 
        "/core/auth/cldkctl",
        "/api/cldkctl/auth"
    ]
    
    for endpoint in endpoints:
        url = production_url + endpoint
        payload = {"token": sample_token}
        
        try:
            resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            print(f"Endpoint {endpoint}: {resp.status_code}")
            if resp.status_code == 200:
                print(f"✅ Found working endpoint: {endpoint}")
                return True
        except Exception as e:
            print(f"Endpoint {endpoint}: Error - {e}")
    
    return False

if __name__ == "__main__":
    test_production_with_fresh_token()
    test_go_cli_behavior() 