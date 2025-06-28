"""
REVIEWER MODULE MIGRATION GUIDE
===============================

This document outlines the migration from reviewer-specific models 
to the unified master models system.

## MODEL MAPPING

Old Reviewer Models → New Master Models:
- Pengguna → master.CustomUser
- ProfileJob → master.JobProfile  
- JobItem → master.JobImage
- Gambar → master.JobImage
- Segmentasi → master.Segmentation
- Anotasi → master.Annotation
- PolygonTool → master.PolygonPoint
- IsuAnotasi → master.AnnotationIssue
- IsuImage → master.ImageAnnotationIssue
- Member → master.CustomUser (role field)
- TipeRole → Use CustomUser.ROLE_CHOICES
- MemberRole → Use CustomUser.role field

## FIELD MAPPING

### User Fields
Old: Pengguna
- id_pengguna → CustomUser.id
- nama_pengguna → CustomUser.username
- nama_lengkap → CustomUser.first_name + last_name
- email → CustomUser.email
- password → CustomUser.password (handled by Django auth)
- is_active → CustomUser.is_active

### Job Fields  
Old: ProfileJob
- id_profile_job → JobProfile.id
- id_pengguna → JobProfile.worker_annotator (or worker_reviewer)
- nama_profile_job → JobProfile.title
- deskripsi → JobProfile.description
- start_date → JobProfile.start_date
- end_date → JobProfile.end_date
- isu → JobProfile.description (or create Issue model entry)

Old: JobItem  
- id_job_item → JobImage.id
- id_profile_job → JobImage.job
- id_gambar → JobImage.id (self-reference)
- status_pekerjaan → JobImage.status

### Annotation Fields
Old: Segmentasi
- id_segmentasi → Segmentation.id
- id_tipe_segmentasi → Segmentation.segmentation_type
- label_segmentasi → Segmentation.label
- warna_segmentasi → Segmentation.color
- koordinat → Store in JSON format
- id_job_item → Segmentation.job

Old: Anotasi
- id_anotasi → Annotation.id
- id_segmentasi → Annotation.segmentation
- id_gambar → Annotation.job_image
- koordinat_x → Annotation.x_coordinate
- koordinat_y → Annotation.y_coordinate
- lebar → Annotation.width
- tinggi → Annotation.height

Old: PolygonTool
- id_polygon_tool → PolygonPoint.id
- id_anotasi → PolygonPoint.annotation
- koordinat_xn → PolygonPoint.x_coordinate
- koordinat_yn → PolygonPoint.y_coordinate

## MIGRATION STEPS

1. **Data Migration**: Create scripts to migrate existing data
2. **View Updates**: Update all reviewer views to use new models
3. **Template Updates**: Update templates to use new field names
4. **URL Updates**: Ensure URLs work with new model structure
5. **Testing**: Comprehensive testing of reviewer functionality

## SAMPLE MIGRATION QUERIES

```python
# Example: Migrate user data
for old_user in Pengguna.objects.all():
    CustomUser.objects.get_or_create(
        username=old_user.nama_pengguna,
        email=old_user.email,
        first_name=old_user.nama_lengkap.split(' ')[0] if old_user.nama_lengkap else '',
        is_active=old_user.is_active,
        role='reviewer'  # Set appropriate role
    )

# Example: Migrate job data  
for old_job in ProfileJob.objects.all():
    user = CustomUser.objects.get(username=old_job.id_pengguna.nama_pengguna)
    JobProfile.objects.get_or_create(
        title=old_job.nama_profile_job,
        description=old_job.deskripsi,
        start_date=old_job.start_date,
        end_date=old_job.end_date,
        worker_reviewer=user
    )
```

## STATUS

✅ Models integrated into master/models.py
✅ Fresh migrations created
⏳ View migration in progress
⏳ Data migration scripts needed
⏳ Template updates needed
⏳ Full testing required
