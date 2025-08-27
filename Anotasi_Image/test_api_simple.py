#!/usr/bin/env python3
import os
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

# Get a master user
User = get_user_model()
master_user = User.objects.filter(role='master').first()

if not master_user:
    print("No master user found!")
    exit(1)

print(f"Testing with user: {master_user.email}")

# Use Django test client for proper authentication
client = Client()
client.force_login(master_user)

# Test the endpoint
response = client.get('/issue-detail/22/')

print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.get('Content-Type', 'Not specified')}")

if response.status_code == 200:
    try:
        import json
        data = response.json()
        print("\n=== API Response ===")
        print(f"Job Title: {data.get('job_title', 'N/A')}")
        print(f"Classes: {data.get('classes', {})}")
        print(f"Segmentation Types: {data.get('segmentation_types', {})}")
        print(f"Status Counts: {data.get('status_counts', {})}")
        print(f"Number of images: {len(data.get('images', []))}")
        
        if data.get('images'):
            first_image = data['images'][0]
            print(f"\nFirst image info:")
            print(f"  URL: {first_image.get('url', 'N/A')}")
            print(f"  Annotator: {first_image.get('annotator', 'N/A')}")
            print(f"  Issue: {first_image.get('issue', 'N/A')}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response.content[:500]}")
else:
    print(f"Error response: {response.content[:200]}")