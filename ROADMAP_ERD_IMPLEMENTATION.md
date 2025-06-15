# ROADMAP IMPLEMENTASI ERD - MASTER WEBSITE
# Target: Mencapai ERD lengkap untuk sistem 3-website
# Current Focus: Master Website sebagai foundation

## FASE 1: MASTER CORE FEATURES (CURRENT - Sudah Ada)
✅ CustomUser - User management dengan roles
✅ Dataset - File upload dan management  
✅ JobProfile - Job creation dan assignment
✅ JobImage - Individual image management

## FASE 2: MASTER ADVANCED FEATURES (PRIORITAS TINGGI)

### Tabel yang Perlu Ditambahkan untuk Master:

1. **Project Management:**
   - Project (untuk grouping multiple jobs)
   - ProjectMember (untuk assign users ke projects)
   
2. **Enhanced Job Management:**
   - JobCategory/JobType (kategorisasi jobs)
   - JobTemplate (template untuk job creation)
   - JobHistory (audit trail job changes)
   
3. **Advanced User Management:**
   - UserProfile (extended user information)
   - UserPermission (granular permissions)
   - Team/Group (untuk organize users)
   
4. **Quality Control:**
   - QualityMetrics (untuk track annotation quality)
   - ReviewCriteria (kriteria review)
   
5. **Reporting & Analytics:**
   - JobStatistics (performance metrics)
   - UserStatistics (individual performance)
   - SystemLogs (audit trails)

## FASE 3: ANNOTATOR INTEGRATION (MEDIUM PRIORITY)

### Tabel untuk Support Annotator Website:
1. **Annotation Workflow:**
   - AnnotationSession (track annotation sessions)
   - AnnotationTool (tool configurations)
   - AnnotationValidation (validation rules)
   
2. **Image Processing:**
   - ImageMetadata (EXIF, dimensions, etc.)
   - ImageAnnotation (annotation data)
   - AnnotationHistory (version control)
   
3. **Task Management:**
   - TaskQueue (task assignment)
   - TaskPriority (prioritization)
   - TaskDeadline (deadline management)

## FASE 4: REVIEWER INTEGRATION (MEDIUM PRIORITY)

### Tabel untuk Support Reviewer Website:
1. **Review Workflow:**
   - ReviewSession (review sessions)
   - ReviewFeedback (feedback dari reviewer)
   - ReviewCriteria (review standards)
   
2. **Quality Assurance:**
   - QualityCheck (quality validation)
   - ReviewMetrics (review performance)
   - ApprovalWorkflow (approval process)

## FASE 5: SYSTEM INTEGRATION (LOW PRIORITY)

### Tabel untuk Full System Integration:
1. **Notification System:**
   - Notification (system notifications)
   - NotificationSettings (user preferences)
   
2. **File Management:**
   - FileStorage (advanced file handling)
   - FileVersion (version control)
   - FileMetadata (file information)
   
3. **System Administration:**
   - SystemSettings (global configurations)
   - BackupLog (backup management)
   - MaintenanceLog (system maintenance)

## PRIORITAS IMMEDIATE UNTUK MASTER WEBSITE:

### Phase 2A: Enhanced Job Management (Minggu 1-2)
```python
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
class JobTemplate(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    default_settings = models.JSONField()
```

### Phase 2B: User & Team Management (Minggu 3-4)
```python
class Team(models.Model):
    name = models.CharField(max_length=255)
    leader = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    members = models.ManyToManyField(CustomUser, through='TeamMembership')

class TeamMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    joined_date = models.DateTimeField(auto_now_add=True)
```

### Phase 2C: Quality & Analytics (Minggu 5-6)
```python
class JobStatistics(models.Model):
    job = models.OneToOneField(JobProfile, on_delete=models.CASCADE)
    total_images = models.IntegerField(default=0)
    completed_images = models.IntegerField(default=0)
    avg_completion_time = models.DurationField(null=True)
    quality_score = models.FloatField(null=True)

class UserPerformance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(JobProfile, on_delete=models.CASCADE)
    images_completed = models.IntegerField(default=0)
    avg_time_per_image = models.DurationField(null=True)
    quality_rating = models.FloatField(null=True)
```

## NEXT STEPS:

1. **Validasi roadmap** ini dengan kebutuhan Master website Anda
2. **Pilih Phase 2A/2B/2C** mana yang paling urgent
3. **Implement step-by-step** untuk avoid breaking current functionality
4. **Test integration** dengan Annotator/Reviewer nanti

Mana yang ingin kita mulai implementasikan dulu? 🚀
