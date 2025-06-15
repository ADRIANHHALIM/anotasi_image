# ANALISIS DETAIL ERD ACUAN - MASTER, ANNOTATOR, REVIEWER SYSTEM
# Date: June 16, 2025
# Target: Full schema analysis untuk PostgreSQL implementation

## IDENTIFIKASI TABEL DARI ERD ACUAN

### KATEGORI 1: USER MANAGEMENT & AUTHENTICATION
```
1. auth_user - Core Django user table
2. auth_user_groups - User group memberships
3. auth_group - User groups/roles
4. auth_group_permissions - Group permissions
5. auth_permission - System permissions
6. auth_user_user_permissions - Individual user permissions
```

### KATEGORI 2: DJANGO FRAMEWORK TABLES
```
7. django_admin_log - Admin action logs
8. django_content_type - Content type framework
9. django_migrations - Migration history
10. django_session - Session management
```

### KATEGORI 3: PROJECT & DATASET MANAGEMENT (MASTER FOCUS)
```
11. master_dataset - Dataset management
12. master_project - Project grouping
13. master_projectmember - Project team assignments
14. master_jobprofile - Job definitions
15. master_jobimage - Individual images
```

### KATEGORI 4: ANNOTATION WORKFLOW (ANNOTATOR FOCUS)
```
16. annotator_annotation - Annotation data
17. annotator_annotationsession - Work sessions
18. annotator_task - Task assignments
19. annotator_taskqueue - Task distribution
20. annotator_imageannotation - Image-specific annotations
```

### KATEGORI 5: REVIEW WORKFLOW (REVIEWER FOCUS)
```
21. reviewer_review - Review records
22. reviewer_reviewsession - Review sessions
23. reviewer_feedback - Review feedback
24. reviewer_qualitycheck - Quality validation
25. reviewer_approval - Approval workflow
```

### KATEGORI 6: ADVANCED FEATURES
```
26. notification_system - Notifications
27. file_management - File handling
28. system_settings - Global settings
29. audit_logs - System audit trail
30. performance_metrics - Analytics
```

## MAPPING KE CURRENT DJANGO MODELS

### EXISTING (Yang sudah ada):
```python
✅ CustomUser ≈ auth_user (extended)
✅ Dataset ≈ master_dataset
✅ JobProfile ≈ master_jobprofile  
✅ JobImage ≈ master_jobimage
```

### MISSING (Yang perlu ditambahkan):
```python
❌ Project management tables
❌ Task & queue management
❌ Annotation workflow tables
❌ Review workflow tables
❌ Permission & role management
❌ Notification system
❌ Performance tracking
```

## PRIORITAS IMPLEMENTASI BERDASARKAN ERD

### PHASE 1: MASTER WEBSITE FOUNDATION (IMMEDIATE)
```sql
-- Project Management
CREATE TABLE master_project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES auth_user(id),
    created_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50),
    deadline DATE
);

-- Enhanced Job Management  
ALTER TABLE master_jobprofile ADD COLUMN project_id INTEGER REFERENCES master_project(id);
ALTER TABLE master_jobprofile ADD COLUMN priority VARCHAR(20);
ALTER TABLE master_jobprofile ADD COLUMN estimated_duration INTERVAL;

-- Team Management
CREATE TABLE master_team (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    leader_id INTEGER REFERENCES auth_user(id),
    project_id INTEGER REFERENCES master_project(id)
);

CREATE TABLE master_teammembership (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    team_id INTEGER REFERENCES master_team(id),
    role VARCHAR(50),
    joined_date TIMESTAMP DEFAULT NOW()
);
```

### PHASE 2: ANNOTATOR INTEGRATION (NEXT)
```sql
-- Task Management
CREATE TABLE annotator_task (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES master_jobprofile(id),
    assignee_id INTEGER REFERENCES auth_user(id),
    status VARCHAR(50),
    priority INTEGER,
    created_date TIMESTAMP DEFAULT NOW(),
    deadline TIMESTAMP
);

-- Annotation Data
CREATE TABLE annotator_annotation (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES master_jobimage(id),
    annotator_id INTEGER REFERENCES auth_user(id),
    annotation_data JSONB,
    created_date TIMESTAMP DEFAULT NOW(),
    modified_date TIMESTAMP DEFAULT NOW()
);
```

### PHASE 3: REVIEWER INTEGRATION (LATER)
```sql
-- Review Workflow
CREATE TABLE reviewer_review (
    id SERIAL PRIMARY KEY,
    annotation_id INTEGER REFERENCES annotator_annotation(id),
    reviewer_id INTEGER REFERENCES auth_user(id),
    status VARCHAR(50),
    feedback TEXT,
    quality_score INTEGER,
    reviewed_date TIMESTAMP DEFAULT NOW()
);
```

## POSTGRESQL SPECIFIC ADVANTAGES

### JSON Support untuk Annotation Data:
```python
class Annotation(models.Model):
    image = models.ForeignKey(JobImage, on_delete=models.CASCADE)
    annotation_data = models.JSONField()  # PostgreSQL native JSON
    metadata = models.JSONField(default=dict)
```

### Full-text Search:
```python
from django.contrib.postgres.search import SearchVector

# Search dalam annotations
JobProfile.objects.annotate(
    search=SearchVector('title', 'description')
).filter(search='image classification')
```

### Array Fields:
```python
class JobProfile(models.Model):
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    allowed_formats = ArrayField(models.CharField(max_length=10), default=list)
```

## NEXT STEPS IMPLEMENTATION:

1. **Setup PostgreSQL** dengan schema yang sesuai ERD
2. **Migrate existing SQLite data** ke PostgreSQL
3. **Implement missing models** sesuai prioritas
4. **Create proper relationships** antar tabel
5. **Setup indexes** untuk performance
6. **Prepare for Annotator/Reviewer integration**

## QUESTIONS UNTUK VALIDASI:

1. **Apakah tabel-tabel yang saya identifikasi** sesuai dengan yang Anda lihat di ERD?
2. **Mana yang paling prioritas** untuk Master website?
3. **Bagaimana struktur collaboration** dengan tim Annotator?

Ready untuk start PostgreSQL migration dengan schema yang comprehensive? 🚀
