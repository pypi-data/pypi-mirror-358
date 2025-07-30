#!/usr/bin/env python3
"""
Detailed comparison between production and staging authentication.
"""

import requests
import json
import time

def test_endpoint(url, token, description):
    """Test an endpoint and return detailed results."""
    print(f"\n=== Testing {description} ===")
    print(f"URL: {url}")
    print(f"Token: {token[:20]}...")
    
    payload = {"token": token}
    headers = {'Content-Type': 'application/json'}
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        print(f"Response Time: {end_time - start_time:.2f}s")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            try:
                data = response.json()
                jwt_token = data.get("data", {}).get("token")
                if jwt_token:
                    print(f"✅ SUCCESS! JWT Token: {jwt_token[:50]}...")
                    return True
                else:
                    print("❌ No JWT token in response")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    return False
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
                print(f"Response: {response.text[:500]}...")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    token = "cldkctl_Np5ShM0TQKFTHRxGqFISxlrzcv7UqpDA"
    
    # Test production
    production_url = "https://ai.cloudeka.id/core/cldkctl/auth"
    production_success = test_endpoint(production_url, token, "PRODUCTION")
    
    # Test staging
    staging_url = "https://staging.ai.cloudeka.id/core/cldkctl/auth"
    staging_success = test_endpoint(staging_url, token, "STAGING")
    
    print(f"\n=== SUMMARY ===")
    print(f"Production: {'✅ SUCCESS' if production_success else '❌ FAILED'}")
    print(f"Staging: {'✅ SUCCESS' if staging_success else '❌ FAILED'}")
    
    if production_success and staging_success:
        print("Both environments work! The issue might be intermittent.")
    elif staging_success and not production_success:
        print("Staging works but production doesn't. This suggests a backend issue.")
    elif production_success and not staging_success:
        print("Production works but staging doesn't. This is unexpected.")
    else:
        print("Neither environment works. The token might be invalid or expired.")

if __name__ == "__main__":
    main() 