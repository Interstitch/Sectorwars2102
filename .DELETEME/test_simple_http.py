#!/usr/bin/env python3
"""
Simple HTTP request tester to diagnose network connectivity issues.
Tests different kinds of HTTP requests to verify what's working and what's not.
"""
import sys
import os
import requests
import json
import platform
import socket
from urllib.parse import urlparse

print("===== Simple HTTP Request Tester =====")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")

# Try to get hostname
try:
    hostname = socket.gethostname()
    print(f"Hostname: {hostname}")
except Exception as e:
    print(f"Could not get hostname: {e}")

# Get environment details
print("\n=== Environment Variables ===")
codespace_name = os.environ.get("CODESPACE_NAME", "Not set")
print(f"CODESPACE_NAME: {codespace_name}")
print(f"GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN: {os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'Not set')}")

# Test different URLs
test_urls = [
    "https://www.google.com",
    "https://www.github.com",
    "http://localhost:8080/api/v1/status",
]

# Add Codespaces-specific URL if running in Codespaces
if codespace_name:
    test_urls.append(f"https://{codespace_name}-8080.app.github.dev/api/v1/status")

# Function to format response preview
def format_response(response):
    try:
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            return json.dumps(response.json(), indent=2)
        else:
            text = response.text[:200]
            if len(response.text) > 200:
                text += "..."
            return text
    except Exception as e:
        return f"Could not format response: {e}"

# Test each URL
print("\n=== Testing URLs ===")
for url in test_urls:
    print(f"\nTesting: {url}")
    try:
        parsed_url = urlparse(url)
        print(f"  Scheme: {parsed_url.scheme}")
        print(f"  Netloc: {parsed_url.netloc}")
        print(f"  Path: {parsed_url.path}")
        
        response = requests.get(url, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        print(f"  Response Preview: {format_response(response)}")
    except requests.RequestException as e:
        print(f"  Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response status: {e.response.status_code}")
            print(f"  Response headers: {dict(e.response.headers)}")
    except Exception as e:
        print(f"  Unexpected error: {e}")

# Test DNS resolution
print("\n=== Testing DNS Resolution ===")
domains_to_test = ["www.google.com", "www.github.com"]
if codespace_name:
    domains_to_test.append(f"{codespace_name}-8080.app.github.dev")

for domain in domains_to_test:
    print(f"\nResolving: {domain}")
    try:
        ip_addresses = socket.gethostbyname_ex(domain)
        print(f"  Result: {ip_addresses}")
    except socket.gaierror as e:
        print(f"  DNS lookup failed: {e}")
    except Exception as e:
        print(f"  Unexpected error: {e}")

print("\n===== Test Complete =====")