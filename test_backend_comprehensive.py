#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://ttprov4-k58o.onrender.com"

print("=== COMPREHENSIVE BACKEND TEST ===\n")

# Test 1: Basic health check
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Check API docs
print("\n2. Testing API docs...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test CORS preflight
print("\n3. Testing CORS preflight...")
try:
    response = requests.options(
        f"{BASE_URL}/auth/register",
        headers={
            "Origin": "https://www.titletesterpro.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for header, value in response.headers.items():
        if "access-control" in header.lower():
            print(f"     {header}: {value}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Test register without token
print("\n4. Testing register without token...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"test": "data"},
        headers={"Origin": "https://www.titletesterpro.com"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Test OAuth config
print("\n5. Testing OAuth config...")
try:
    response = requests.get(f"{BASE_URL}/auth/oauth/config")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 6: Check specific failing endpoints
failing_endpoints = [
    ("GET", "/api/ab-tests/"),
    ("GET", "/api/channels/"),
    ("POST", "/api/channels/sync"),
    ("GET", "/api/ab-tests/channel/videos?max_results=50")
]

print("\n6. Testing failing endpoints...")
for method, endpoint in failing_endpoints:
    print(f"\n   {method} {endpoint}")
    try:
        if method == "GET":
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={
                    "Origin": "https://www.titletesterpro.com",
                    "Authorization": "Bearer fake-token-for-test"
                }
            )
        else:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json={},
                headers={
                    "Origin": "https://www.titletesterpro.com",
                    "Authorization": "Bearer fake-token-for-test"
                }
            )
        print(f"     Status: {response.status_code}")
        if response.status_code < 500:
            try:
                print(f"     Response: {response.json()}")
            except:
                print(f"     Response: {response.text[:100]}...")
        else:
            print(f"     ERROR: Internal Server Error")
            print(f"     Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"     ERROR: {e}")

print("\n=== END OF TEST ===")