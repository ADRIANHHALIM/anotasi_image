#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/adrianhalim/Documents/anotasi_image/Anotasi_Image')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

from master.models import JobProfile, JobImage, Annotation, Segmentation

def check_job_annotations():
    print("=== CHECKING ANNOTATIONS FOR JOB ID 22 ===")
    
    try:
        # Get job
        job = JobProfile.objects.get(id=22)
        print(f"Job found: {job.title}")
        
        # Get all images for this job
        job_images = JobImage.objects.filter(job=job)
        print(f"Total images in job: {job_images.count()}")
        
        for img in job_images:
            print(f"\n--- IMAGE {img.id} ---")
            print(f"Filename: {img.image.name if img.image else 'No file'}")
            print(f"Status: {img.status}")
            
            # Check annotations for this image
            annotations = Annotation.objects.filter(job_image=img)
            print(f"Annotations count: {annotations.count()}")
            
            if annotations.exists():
                for ann in annotations:
                    print(f"  Annotation {ann.id}:")
                    print(f"    Label: {ann.label}")
                    print(f"    Coordinates: x_min={ann.x_min}, y_min={ann.y_min}, x_max={ann.x_max}, y_max={ann.y_max}")
                    print(f"    Status: {ann.status}")
                    if ann.segmentation:
                        print(f"    Segmentation label: {ann.segmentation.label}")
                        print(f"    Segmentation color: {ann.segmentation.color}")
                    else:
                        print(f"    No segmentation linked")
            else:
                print("  ❌ No annotations found for this image")
                
    except JobProfile.DoesNotExist:
        print("❌ Job with ID 22 not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== CHECKING OVERALL ANNOTATION STATISTICS ===")
    total_annotations = Annotation.objects.count()
    total_segmentations = Segmentation.objects.count()
    print(f"Total annotations in database: {total_annotations}")
    print(f"Total segmentations in database: {total_segmentations}")
    
    # Check if there are any annotations for any job
    jobs_with_annotations = JobProfile.objects.filter(images__annotations__isnull=False).distinct()
    print(f"Jobs with annotations: {jobs_with_annotations.count()}")
    
    for job in jobs_with_annotations:
        ann_count = Annotation.objects.filter(job_image__job=job).count()
        print(f"  Job {job.id} ({job.title}): {ann_count} annotations")

if __name__ == "__main__":
    check_job_annotations()