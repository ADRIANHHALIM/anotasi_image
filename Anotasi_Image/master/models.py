from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.db.models.functions import Cast
import os

<<<<<<< HEAD
class User(models.Model):
    ROLE_CHOICES = [
        ('annotator', 'Annotator'),
        ('master', 'Master'),
        ('reviewer', 'Reviewer'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='annotator')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
=======
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
    date_created = models.DateTimeField(auto_now_add=True)
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
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    segmentation_type = models.CharField(max_length=20, choices=SEGMENTATION_CHOICES)
    shape_type = models.CharField(max_length=20, choices=SHAPE_CHOICES)
    color = models.CharField(max_length=7)  # For hex color codes
    start_date = models.DateField()
    end_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    estimated_duration = models.DurationField(null=True, blank=True)
    project_id = models.BigIntegerField(null=True, blank=True)
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
        ('annotated', 'Annotated'),
        ('in_review', 'In Review'),
        ('in_rework', 'In Rework'),
        ('finished', 'Finished'),
        ('Issue', 'Issue'),  # Make sure 'Issue' is exactly as used in the filter
    ]
    
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=job_image_path)
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

class Issue(models.Model):
    """
    Model untuk issue/masalah yang ditemukan oleh master atau reviewer 
    pada hasil anotasi dari annotator
    """
    ISSUE_STATUS_CHOICES = [
        ('open', 'Open'),
        ('eskalasi', 'Eskalasi'),
        ('reworking', 'Reworking'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Brief title of the issue")
    description = models.TextField(help_text="Detailed description of the issue")
    status = models.CharField(max_length=20, choices=ISSUE_STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Relationships
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='issues')
    image = models.ForeignKey(JobImage, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_issues', 
                                   help_text="Annotator yang harus menangani issue ini")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_issues',
                                  help_text="Master/Reviewer yang membuat issue ini")
    
    # Additional Information
    annotation_id = models.CharField(max_length=100, null=True, blank=True, 
                                   help_text="ID spesifik annotation yang bermasalah")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['job', 'assigned_to']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Issue #{self.id}: {self.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto set resolved_at when status changes to closed
        if self.status == 'closed' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'closed':
            self.resolved_at = None
        super().save(*args, **kwargs)


class IssueComment(models.Model):
    """
    Model untuk komentar/diskusi pada issue
    """
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.created_by.username} on Issue #{self.issue.id}"


class IssueAttachment(models.Model):
    """
    Model untuk file attachment pada issue (screenshot, annotated image, etc.)
    """
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='issue_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment: {self.filename} for Issue #{self.issue.id}"

class Notification(models.Model):
    """
    Model untuk notifikasi kepada annotator
    """
    NOTIFICATION_TYPES = [
        ('job_assigned', 'Job Assigned'),
        ('job_updated', 'Job Updated'),
        ('issue_created', 'Issue Created'),
        ('issue_updated', 'Issue Updated'),
        ('job_deadline', 'Job Deadline'),
    ]
    
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
    
    def get_task_id(self):
        """Generate task ID similar to screenshot"""
        if self.job:
            # Create task ID like: 123456712345544523234
            return f"{self.job.id}{self.id}{self.created_at.strftime('%Y%m%d%H%M%S')}"
        return f"{self.id}{self.created_at.strftime('%Y%m%d%H%M%S')}"
    
    def get_time_display(self):
        """Get human readable time like '30 minutes ago'"""
        from django.utils.timesince import timesince
        return f"{timesince(self.created_at)} ago"
>>>>>>> 25292504d23e7f8e25be5caa7222ee2190cf9cff
