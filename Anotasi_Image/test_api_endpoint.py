#!/usr/bin/env python
import requests
import json

# Test the issue-detail API endpoint
url = "http://localhost:8001/issue-detail/22/"

try:
    # Create a session
    session = requests.Session()
    
    # First, get the login page to get CSRF token
    login_page = session.get("http://localhost:8001/login/")
    
    # Try to access the API endpoint
    response = session.get(url, headers={
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\n=== API Response ===")
            print(f"Job Title: {data.get('job_title', 'N/A')}")
            print(f"Number of images: {len(data.get('images', []))}")
            print(f"Classes: {list(data.get('classes', {}).keys())}")
            print(f"Segmentation types: {list(data.get('segmentation_types', {}).keys())}")
            
            if data.get('images'):
                print("\n=== First Image Info ===")
                first_img = data['images'][0]
                print(f"URL: {first_img.get('url', 'N/A')}")
                print(f"Status: {first_img.get('status', 'N/A')}")
                print(f"Annotations: {len(first_img.get('annotations', []))}")
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print(f"Response content (first 500 chars): {response.text[:500]}")
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Error: {e}")