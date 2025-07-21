"""
DATA MIGRATION SCRIPT
====================

This script helps migrate existing reviewer data to the new master models.
Run this AFTER applying the model migrations but BEFORE deleting old data.

Usage:
1. Backup your database first!
2. python manage.py shell
3. exec(open('data_migration_script.py').read())
"""

from master.models import (
    CustomUser, JobProfile, JobImage, 
    SegmentationType, Segmentation, Annotation, 
    PolygonPoint, AnnotationIssue, ImageAnnotationIssue
)

def migrate_reviewer_data():
    """
    Migrate data from old reviewer models to new master models
    Only run this if you have existing data to migrate
    """
    print("Starting data migration...")
    
    # Note: This is a template - adjust based on your actual old model structure
    # You would need to import the old models if they still exist
    
    try:
        # Example migration for user data
        # Old: Pengguna → New: CustomUser
        # from reviewer.models import Pengguna  # If old models still exist
        # for old_user in Pengguna.objects.all():
        #     CustomUser.objects.get_or_create(
        #         username=old_user.nama_pengguna,
        #         email=old_user.email,
        #         defaults={
        #             'first_name': old_user.nama_lengkap.split()[0] if old_user.nama_lengkap else '',
        #             'last_name': ' '.join(old_user.nama_lengkap.split()[1:]) if old_user.nama_lengkap else '',
        #             'is_active': old_user.is_active,
        #             'role': 'reviewer'
        #         }
        #     )
        
        # Example migration for job profiles
        # Old: ProfileJob → New: JobProfile
        # from reviewer.models import ProfileJob  # If old models still exist
        # for old_profile in ProfileJob.objects.all():
        #     user = CustomUser.objects.get(id=old_profile.id_pengguna)
        #     JobProfile.objects.get_or_create(
        #         title=old_profile.nama_profile_job,
        #         defaults={
        #             'description': old_profile.deskripsi,
        #             'worker_reviewer': user,
        #             'start_date': old_profile.start_date,
        #             'end_date': old_profile.end_date,
        #             'color': old_profile.warna,
        #             'segmentation_type': 'semantic',  # Default value
        #             'shape_type': 'polygon'  # Default value
        #         }
        #     )
        
        print("Data migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        print("This is expected if no old data exists or models have been removed.")

def create_default_segmentation_types():
    """Create default segmentation types if they don't exist"""
    types = ['Semantic', 'Instance', 'Panoptic']
    for type_name in types:
        SegmentationType.objects.get_or_create(name=type_name)
    print("Default segmentation types created!")

def verify_migration():
    """Verify that the migration was successful"""
    print("\n=== MIGRATION VERIFICATION ===")
    print(f"CustomUser count: {CustomUser.objects.count()}")
    print(f"JobProfile count: {JobProfile.objects.count()}")
    print(f"JobImage count: {JobImage.objects.count()}")
    print(f"SegmentationType count: {SegmentationType.objects.count()}")
    print(f"Segmentation count: {Segmentation.objects.count()}")
    print(f"Annotation count: {Annotation.objects.count()}")
    print(f"PolygonPoint count: {PolygonPoint.objects.count()}")
    print(f"AnnotationIssue count: {AnnotationIssue.objects.count()}")
    print(f"ImageAnnotationIssue count: {ImageAnnotationIssue.objects.count()}")

if __name__ == "__main__":
    create_default_segmentation_types()
    # migrate_reviewer_data()  # Uncomment if you have data to migrate
    verify_migration()
