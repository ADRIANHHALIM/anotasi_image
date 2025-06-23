# PROPOSAL: Issue Model untuk Issue Tracking System
# File ini berisi proposal model yang bisa ditambahkan ke master/models.py

"""
class Issue(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    ISSUE_TYPE_CHOICES = [
        ('annotation_quality', 'Annotation Quality'),
        ('missing_annotation', 'Missing Annotation'),
        ('wrong_label', 'Wrong Label'),
        ('technical_issue', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    # Core fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, default='annotation_quality')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Relationships
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='issues')
    image = models.ForeignKey(JobImage, on_delete=models.CASCADE, related_name='issues')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_issues')  # Usually reviewer
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_issues')  # Usually annotator
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    estimated_fix_time = models.DurationField(null=True, blank=True)
    actual_fix_time = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
    
    def __str__(self):
        return f"Issue #{self.id}: {self.title}"
    
    def save(self, *args, **kwargs):
        # Auto-set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)


class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Attachment support
    attachment = models.FileField(upload_to='issue_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on Issue #{self.issue.id} by {self.created_by.username}"


class IssueAttachment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='issue_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment: {self.filename}"
"""

# WORKFLOW INTEGRATION:
# 1. Reviewer finds issue → Creates Issue object with status='open'
# 2. JobImage status automatically changes to 'in_rework' 
# 3. Annotator gets notification → Views issue in Issues tab
# 4. Annotator clicks "Start Work" → Issue status changes to 'in_progress'
# 5. Annotator fixes and clicks "Mark Resolved" → Issue status = 'resolved'
# 6. JobImage status changes back to 'annotated' for re-review
# 7. Reviewer reviews again → If OK, marks Issue as 'closed' and JobImage as 'finished'

# MIGRATION COMMAND:
# python manage.py makemigrations master
# python manage.py migrate

# ADMIN INTEGRATION:
# Add to master/admin.py:
# from .models import Issue, IssueComment, IssueAttachment
# 
# @admin.register(Issue)
# class IssueAdmin(admin.ModelAdmin):
#     list_display = ['id', 'title', 'issue_type', 'priority', 'status', 'created_by', 'assigned_to', 'created_at']
#     list_filter = ['status', 'priority', 'issue_type', 'created_at']
#     search_fields = ['title', 'description']
#     ordering = ['-created_at']
# 
# @admin.register(IssueComment)
# class IssueCommentAdmin(admin.ModelAdmin):
#     list_display = ['issue', 'created_by', 'message', 'created_at']
#     list_filter = ['created_at']
