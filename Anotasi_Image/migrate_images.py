#!/usr/bin/env python
"""
Script untuk migrasi gambar ke folder berdasarkan job ID
"""
import os
import shutil
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

from master.models import JobImage

def migrate_images():
    """Migrate existing images to job-specific folders"""
    
    media_root = settings.MEDIA_ROOT
    job_images_path = os.path.join(media_root, 'job_images')
    
    print(f"Media root: {media_root}")
    print(f"Job images path: {job_images_path}")
    
    # Get all job images
    images = JobImage.objects.all()
    
    for img in images:
        old_path = os.path.join(media_root, img.image.name)
        
        # Create new path with job_id folder
        job_folder = f"job_{img.job.id}"
        new_folder_path = os.path.join(job_images_path, job_folder)
        
        # Get filename from old path
        filename = os.path.basename(img.image.name)
        new_path = os.path.join(new_folder_path, filename)
        
        print(f"\nProcessing Image ID: {img.id}")
        print(f"Job ID: {img.job.id}")
        print(f"Old path: {old_path}")
        print(f"New path: {new_path}")
        
        # Check if old file exists
        if not os.path.exists(old_path):
            print(f"  ❌ Old file doesn't exist: {old_path}")
            continue
            
        # Create job folder if it doesn't exist
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            print(f"  📁 Created folder: {new_folder_path}")
        
        # Check if new file already exists
        if os.path.exists(new_path):
            print(f"  ⚠️  New file already exists: {new_path}")
            continue
            
        try:
            # Move the file
            shutil.move(old_path, new_path)
            print(f"  ✅ Moved successfully")
            
            # Update the database record
            new_db_path = f"job_images/{job_folder}/{filename}"
            img.image.name = new_db_path
            img.save()
            print(f"  💾 Updated database: {new_db_path}")
            
        except Exception as e:
            print(f"  ❌ Error moving file: {e}")

if __name__ == "__main__":
    print("🚀 Starting image migration...")
    migrate_images()
    print("\n✨ Migration completed!")
