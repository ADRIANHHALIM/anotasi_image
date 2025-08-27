#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

from master.models import *

print('=== JobImage 6 ===')
try:
    ji = JobImage.objects.get(id=6)
    print(f'JobImage: {ji}')
    print(f'Status: {ji.status}')
except JobImage.DoesNotExist:
    print('JobImage 6 not found')
    exit()

print('\n=== Annotations ===')
anns = Annotation.objects.filter(job_image=ji)
print(f'Total annotations: {anns.count()}')
for a in anns:
    print(f'Annotation {a.id}: segmentation={a.segmentation}, label={a.label}')
    if a.segmentation:
        print(f'  - Segmentation type: {a.segmentation.segmentation_type.name}')
        print(f'  - Segmentation label: {a.segmentation.label}')
        print(f'  - Segmentation color: {a.segmentation.color}')

print('\n=== Segmentations ===')
segs = Segmentation.objects.filter(job=ji)
print(f'Total segmentations: {segs.count()}')
for s in segs:
    print(f'Segmentation {s.id}: {s.label} ({s.segmentation_type.name})')

print('\n=== PolygonPoints ===')
for a in anns:
    points_count = a.polygon_points.count()
    print(f'Annotation {a.id} has {points_count} polygon points')
    if points_count > 0:
        for p in a.polygon_points.all().order_by('order'):
            print(f'  Point {p.order}: ({p.x_coordinate}, {p.y_coordinate})')

print('\n=== SegmentationType ===')
seg_types = SegmentationType.objects.all()
for st in seg_types:
    print(f'SegmentationType: {st.name}')