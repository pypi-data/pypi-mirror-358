#!/usr/bin/env python3
"""
Test authentication with the provided token
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_with_token(token):
    """Test authentication with the provided token"""
    
    print(f"🔐 Testing authentication with token: {token[:20]}...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Test both environments with correct endpoints
    environments = [
        {
            "name": "Production",
            "base_url": "https://ai.cloudeka.id",
            "endpoint": "/core/cldkctl/auth"
        },
        {
            "name": "Staging", 
            "base_url": "https://staging.ai.cloudeka.id",
            "endpoint": "/core/cldkctl/auth"
        }
    ]
    
    for env in environments:
        print(f"\n🌐 Testing {env['name']} environment...")
        print(f"   URL: {env['base_url']}{env['endpoint']}")
        
        try:
            # Test authentication endpoint
            auth_url = f"{env['base_url']}{env['endpoint']}"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MCP-CLDKCTL-Test/1.0"
            }
            
            payload = {
                "token": token
            }
            
            print(f"   📤 Sending request...")
            response = requests.post(
                auth_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   📥 Response Status: {response.status_code}")
            print(f"   📥 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Authentication successful!")
                    print(f"   🔑 JWT Token: {data.get('data', {}).get('token', 'N/A')[:50]}...")
                    print(f"   👤 User: {data.get('data', {}).get('user', {}).get('name', 'N/A')}")
                    print(f"   🏢 Organization: {data.get('data', {}).get('user', {}).get('organization', {}).get('name', 'N/A')}")
                    return True, env['name'], data
                except json.JSONDecodeError:
                    print(f"   ⚠️  Response is not JSON: {response.text[:200]}...")
            else:
                print(f"   ❌ Authentication failed")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {str(e)}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
    
    return False, None, None

def test_api_endpoints(base_url, jwt_token):
    """Test some basic API endpoints"""
    print(f"\n🔍 Testing API endpoints with {base_url}...")
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints (using the actual endpoints from the MCP server)
    test_endpoints = [
        "/core/profile",
        "/core/projects",
        "/core/organization"
    ]
    
    for endpoint in test_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"   📡 Testing: {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Success")
                try:
                    data = response.json()
                    print(f"      📊 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except:
                    print(f"      📄 Response is not JSON")
            else:
                print(f"      ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")

if __name__ == "__main__":
    # Your token
    token = "cldkctl_4Lyn6i2vRslxqQi5d0SiNXN5XHyvGRzU"
    
    # Test authentication
    success, environment, auth_data = test_auth_with_token(token)
    
    if success:
        print(f"\n🎉 Authentication successful with {environment}!")
        
        # Test API endpoints
        if environment == "Production":
            base_url = "https://ai.cloudeka.id"
        else:
            base_url = "https://staging.ai.cloudeka.id"
            
        jwt_token = auth_data.get('data', {}).get('token')
        if jwt_token:
            test_api_endpoints(base_url, jwt_token)
    else:
        print(f"\n❌ Authentication failed with both environments")
        print("Please check your token and try again.") 