#!/usr/bin/env python3
"""
Test script for mcp-cldkctl package
"""

import subprocess
import sys
import os

def test_import():
    """Test that the package can be imported"""
    try:
        import mcp_cldkctl
        print("✅ Package import successful")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

def test_server_import():
    """Test that the server can be imported"""
    try:
        from mcp_cldkctl.server import CldkctlMCPServer
        print("✅ Server import successful")
        return True
    except ImportError as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_server_initialization():
    """Test that the server can be initialized"""
    try:
        from mcp_cldkctl.server import CldkctlMCPServer
        server = CldkctlMCPServer()
        print("✅ Server initialization successful")
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

def test_uvx_command():
    """Test that the package can be run with uvx"""
    try:
        # Test if uvx is available
        result = subprocess.run(
            ["uvx", "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode != 0:
            print("❌ uvx not available")
            return False
        
        # Test if our package is available
        result = subprocess.run(
            ["uvx", "mcp-cldkctl", "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ uvx command successful")
            return True
        else:
            print(f"❌ uvx command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ uvx command timed out")
        return False
    except FileNotFoundError:
        print("❌ uvx not found in PATH")
        return False
    except Exception as e:
        print(f"❌ uvx command error: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling"""
    try:
        from mcp_cldkctl.server import CldkctlMCPServer
        
        # Test with no environment variables
        server = CldkctlMCPServer()
        
        # Test with environment variables
        os.environ['CLDKCTL_TOKEN'] = 'test_token'
        os.environ['CLDKCTL_BASE_URL'] = 'https://test.cloudeka.id'
        
        server2 = CldkctlMCPServer()
        
        print("✅ Environment variable handling successful")
        return True
    except Exception as e:
        print(f"❌ Environment variable handling failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing mcp-cldkctl package...")
    print("=" * 50)
    
    tests = [
        ("Package Import", test_import),
        ("Server Import", test_server_import),
        ("Server Initialization", test_server_initialization),
        ("Environment Variables", test_environment_variables),
        ("uvx Command", test_uvx_command),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 