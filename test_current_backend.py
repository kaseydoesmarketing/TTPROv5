#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://ttprov4-k58o.onrender.com"

print("=== CURRENT BACKEND STATE TEST ===\n")

# Test 1: Basic health
print("1. Health check:")
resp = requests.get(f"{BASE_URL}/health")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}\n")

# Test 2: OAuth config (no auth needed)
print("2. OAuth config:")
resp = requests.get(f"{BASE_URL}/auth/oauth/config")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}\n")

# Test 3: Unauthenticated API call
print("3. API call without auth:")
resp = requests.get(f"{BASE_URL}/api/channels/", headers={"Origin": "https://www.titletesterpro.com"})
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}")
print(f"   CORS header: {resp.headers.get('access-control-allow-origin')}\n")

# Test 4: API call with fake token
print("4. API call with fake token:")
resp = requests.get(
    f"{BASE_URL}/api/channels/", 
    headers={
        "Origin": "https://www.titletesterpro.com",
        "Authorization": "Bearer fake-token-12345"
    }
)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}")
print(f"   Content-Type: {resp.headers.get('content-type')}")
print(f"   CORS header: {resp.headers.get('access-control-allow-origin')}\n")

# Test 5: Register endpoint with fake token
print("5. Register with fake token:")
resp = requests.post(
    f"{BASE_URL}/auth/register",
    json={"access_token": "test", "refresh_token": "test"},
    headers={
        "Origin": "https://www.titletesterpro.com",
        "Authorization": "Bearer fake-token-12345",
        "Content-Type": "application/json"
    }
)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}")
print(f"   Content-Type: {resp.headers.get('content-type')}")
print(f"   CORS header: {resp.headers.get('access-control-allow-origin')}")