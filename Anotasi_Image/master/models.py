from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.db.models.functions import Cast

class CustomUserManager(BaseUserManager):
    """Custom manager untuk model CustomUser agar mendukung login dengan email atau username."""

    def get_by_natural_key(self, username):
        # Try to fetch by email first
        try:
            return self.get(email=username)
        except self.model.DoesNotExist:
            # If not found, try username
            return self.get(username=username)
        
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email harus diisi!")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Superuser langsung aktif
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    """Model user kustom dengan tambahan email sebagai field unik dan nomor HP."""
    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('annotator', 'Annotator'),
        ('reviewer', 'Reviewer'),
        ('member', 'Member'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Changed to True
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def save(self, *args, **kwargs):
        # Ensure the user is active when saved
        self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    labeler = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    file_path = models.FileField(upload_to='datasets/')
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class JobProfile(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_count = models.IntegerField(default=0)
    SEGMENTATION_CHOICES = [
        ('semantic', 'Semantic'),
        ('instance', 'Instance'),
        ('panoptic', 'Panoptic')
    ]
    SHAPE_CHOICES = [
        ('bounding_box', 'Bounding Box'),
        ('polygon', 'Polygon')
    ]
    STATUS_CHOICES = [
        ('not_assign', 'Not Assigned'),
        ('in_progress', 'In Progress'),
        ('finish', 'Finished')
    ]
    segmentation_type = models.CharField(max_length=20, choices=SEGMENTATION_CHOICES)
    shape_type = models.CharField(max_length=20, choices=SHAPE_CHOICES)
    color = models.CharField(max_length=7)  # For hex color codes
    start_date = models.DateField()
    end_date = models.DateField()
    worker_annotator = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='annotator_jobs'
    )
    worker_reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewer_jobs'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_assign', 'Not Assigned'),
            ('in_progress', 'In Progress'),
            ('finish', 'Finished')
        ],
        default='not_assign'
    )
    
    def __str__(self):
        return self.title

    def get_first_image_url(self):
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None

def job_image_path(instance, filename):
    # Generate path like: job_images/1/image.jpg
    """
    Generates a file path for a job image based on its associated job ID and filename.
    
    Args:
        instance: The JobImage instance containing the related job.
        filename: The original name of the uploaded image file.
    
    Returns:
        A string representing the storage path in the format 'job_images/{job_id}/{filename}'.
    """
    return f'job_images/{instance.job.id}/{filename}'

class JobImage(models.Model):
    STATUS_CHOICES = [
        ('unannotated', 'Unannotated'),
        ('in_review', 'In Review'),
        ('in_rework', 'In Rework'),
        ('finished', 'Finished'),
        ('Issue', 'Issue'),  # Make sure 'Issue' is exactly as used in the filter
    ]
    
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='job_images/')
    annotator = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='annotated_images'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unannotated'
    )
    issue_description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add these fields for timing information
    label_time = models.DurationField(null=True, blank=True)
    review_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the image with its ID and associated job title.
        """
        return f"Image {self.id} for Job {self.job.title}"

    def get_image_url(self):
        """
        Returns the URL of the associated image if available, or None if no image is present.
        """
        if self.image:
            return self.image.url
        return None
