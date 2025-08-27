#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
django.setup()

from master.models import Annotation, Segmentation, SegmentationType, AnnotationTool

print('=== FIXING EXISTING ANNOTATIONS ===')

# Get or create segmentation type
segmentation_type, created = SegmentationType.objects.get_or_create(
    name='instance',
    defaults={'description': 'Instance segmentation for object detection'}
)
print(f'Segmentation type: {segmentation_type.name} (created: {created})')

# Get or create annotation tool
annotation_tool, created = AnnotationTool.objects.get_or_create(
    name='AI Detection',
    defaults={'description': 'Automatic AI-based object detection'}
)
print(f'Annotation tool: {annotation_tool.name} (created: {created})')

# Fix annotations without segmentation
annotations_without_segmentation = Annotation.objects.filter(segmentation__isnull=True)
print(f'Found {annotations_without_segmentation.count()} annotations without segmentation')

fixed_count = 0
for annotation in annotations_without_segmentation:
    if annotation.label and annotation.job_image:
        # Create segmentation for this annotation
        segmentation, created = Segmentation.objects.get_or_create(
            job=annotation.job_image,
            label=annotation.label,
            defaults={
                'segmentation_type': segmentation_type,
                'color': f'#{hash(annotation.label) % 0xFFFFFF:06x}',
                'coordinates': f'{annotation.x_min},{annotation.y_min},{annotation.x_max},{annotation.y_max}',
                'description': f'Auto-detected {annotation.label}'
            }
        )
        
        # Update annotation to link to segmentation
        annotation.segmentation = segmentation
        if not annotation.tool:
            annotation.tool = annotation_tool
        annotation.save()
        
        fixed_count += 1
        print(f'Fixed annotation {annotation.id}: {annotation.label} -> segmentation {segmentation.id}')

print(f'\n=== SUMMARY ===')
print(f'Fixed {fixed_count} annotations')
print(f'Total annotations now: {Annotation.objects.count()}')
print(f'Annotations with segmentation: {Annotation.objects.filter(segmentation__isnull=False).count()}')
print(f'Annotations without segmentation: {Annotation.objects.filter(segmentation__isnull=True).count()}')
print(f'Total segmentations: {Segmentation.objects.count()}')