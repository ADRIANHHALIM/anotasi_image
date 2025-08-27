#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

from master.models import Annotation, Segmentation, JobImage

print('=== ANNOTATION DATA ANALYSIS ===')
print(f'Total annotations: {Annotation.objects.count()}')
print(f'Annotations with null segmentation: {Annotation.objects.filter(segmentation__isnull=True).count()}')
print(f'Annotations with segmentation: {Annotation.objects.filter(segmentation__isnull=False).count()}')

print('\n=== SEGMENTATION DATA ===')
print(f'Total segmentations: {Segmentation.objects.count()}')
for s in Segmentation.objects.all()[:10]:
    print(f'ID: {s.id}, Label: "{s.label}", Job: {s.job_id}')

print('\n=== ANNOTATION-SEGMENTATION RELATIONSHIPS ===')
for a in Annotation.objects.all()[:15]:
    seg_label = a.segmentation.label if a.segmentation else 'NULL'
    print(f'Annotation ID: {a.id}, Segmentation: {a.segmentation_id}, Label: "{seg_label}", Job Image: {a.job_image_id}')

print('\n=== ANNOTATIONS BY JOB IMAGE ===')
for job_img in JobImage.objects.all()[:5]:
    annotations = Annotation.objects.filter(job_image=job_img)
    print(f'Job Image {job_img.id}: {annotations.count()} annotations')
    for ann in annotations[:3]:
        seg_label = ann.segmentation.label if ann.segmentation else 'NULL'
        print(f'  - Annotation {ann.id}: Label="{seg_label}"')