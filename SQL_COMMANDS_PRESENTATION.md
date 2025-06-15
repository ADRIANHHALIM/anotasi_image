# 📊 SQL Commands untuk Presentasi - Anotasi Image Project

## 🔍 **DATABASE OVERVIEW**

### Lihat semua tables di database
```sql
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Lihat total records di setiap table
```sql
SELECT 
    schemaname,
    tablename,
    n_tup_ins AS "Total Rows"
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
```

## 👥 **USER MANAGEMENT**

### Lihat semua users dengan detail
```sql
SELECT 
    id,
    username,
    email,
    first_name,
    last_name,
    role,
    is_active,
    date_joined::date as join_date
FROM master_customuser 
ORDER BY date_joined DESC;
```

### Count users by role
```sql
SELECT 
    role,
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_active = true THEN 1 END) as active_users
FROM master_customuser 
GROUP BY role
ORDER BY total_users DESC;
```

### Lihat user activity (recent logins)
```sql
SELECT 
    username,
    email,
    last_login::date as last_login_date,
    is_active
FROM master_customuser 
WHERE last_login IS NOT NULL
ORDER BY last_login DESC;
```

## 💼 **JOB MANAGEMENT**

### Overview semua jobs
```sql
SELECT 
    id,
    title,
    status,
    segmentation_type,
    shape_type,
    start_date,
    end_date,
    image_count,
    worker_annotator_id,
    worker_reviewer_id
FROM master_jobprofile 
ORDER BY start_date DESC;
```

### Job statistics by status
```sql
SELECT 
    status,
    COUNT(*) as total_jobs,
    SUM(image_count) as total_images
FROM master_jobprofile 
GROUP BY status
ORDER BY total_jobs DESC;
```

### Jobs dengan worker assignments
```sql
SELECT 
    jp.title as job_title,
    jp.status,
    jp.image_count,
    ann.email as annotator,
    rev.email as reviewer,
    jp.start_date
FROM master_jobprofile jp
LEFT JOIN master_customuser ann ON jp.worker_annotator_id = ann.id
LEFT JOIN master_customuser rev ON jp.worker_reviewer_id = rev.id
ORDER BY jp.start_date DESC;
```

## 🖼️ **IMAGE PROCESSING**

### Image status overview
```sql
SELECT 
    status,
    COUNT(*) as image_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM master_jobimage 
GROUP BY status
ORDER BY image_count DESC;
```

### Images per job dengan progress
```sql
SELECT 
    jp.title as job_title,
    COUNT(ji.id) as total_images,
    COUNT(CASE WHEN ji.status = 'finished' THEN 1 END) as finished_images,
    COUNT(CASE WHEN ji.status = 'unannotated' THEN 1 END) as pending_images,
    ROUND(
        COUNT(CASE WHEN ji.status = 'finished' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(ji.id), 0), 2
    ) as completion_percentage
FROM master_jobprofile jp
LEFT JOIN master_jobimage ji ON jp.id = ji.job_id
GROUP BY jp.id, jp.title
ORDER BY completion_percentage DESC;
```

### Images dengan issue tracking
```sql
SELECT 
    ji.id,
    jp.title as job_title,
    ji.status,
    ji.issue_description,
    ann.email as annotator,
    ji.updated_at::date as last_updated
FROM master_jobimage ji
JOIN master_jobprofile jp ON ji.job_id = jp.id
LEFT JOIN master_customuser ann ON ji.annotator_id = ann.id
WHERE ji.status = 'Issue' OR ji.issue_description IS NOT NULL
ORDER BY ji.updated_at DESC;
```

## 📊 **PERFORMANCE ANALYTICS**

### Worker productivity analysis
```sql
SELECT 
    u.email as worker,
    u.role,
    COUNT(DISTINCT jp.id) as assigned_jobs,
    SUM(jp.image_count) as total_images_assigned,
    COUNT(CASE WHEN jp.status = 'finish' THEN 1 END) as completed_jobs
FROM master_customuser u
LEFT JOIN master_jobprofile jp ON (
    (u.role = 'annotator' AND jp.worker_annotator_id = u.id) OR
    (u.role = 'reviewer' AND jp.worker_reviewer_id = u.id)
)
WHERE u.role IN ('annotator', 'reviewer')
GROUP BY u.id, u.email, u.role
ORDER BY assigned_jobs DESC;
```

### Daily progress tracking
```sql
SELECT 
    DATE(ji.updated_at) as date,
    COUNT(CASE WHEN ji.status = 'finished' THEN 1 END) as images_completed,
    COUNT(CASE WHEN ji.status = 'in_review' THEN 1 END) as images_in_review,
    COUNT(CASE WHEN ji.status = 'Issue' THEN 1 END) as images_with_issues
FROM master_jobimage ji
WHERE ji.updated_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(ji.updated_at)
ORDER BY date DESC;
```

## 🗂️ **DATASET MANAGEMENT**

### Dataset overview
```sql
SELECT 
    d.name as dataset_name,
    u.email as labeler,
    d.count as image_count,
    d.date_created::date as created_date
FROM master_dataset d
JOIN master_customuser u ON d.labeler_id = u.id
ORDER BY d.date_created DESC;
```

## 🔧 **SYSTEM MONITORING**

### Database size dan table sizes
```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Migration history
```sql
SELECT 
    app,
    name,
    applied::date as applied_date
FROM django_migrations 
ORDER BY applied DESC 
LIMIT 10;
```

## 🚀 **QUICK DEMO QUERIES**

### Project summary untuk presentasi
```sql
SELECT 
    'Total Users' as metric,
    COUNT(*)::text as value
FROM master_customuser
UNION ALL
SELECT 
    'Total Jobs',
    COUNT(*)::text
FROM master_jobprofile
UNION ALL
SELECT 
    'Total Images',
    COUNT(*)::text
FROM master_jobimage
UNION ALL
SELECT 
    'Completion Rate',
    ROUND(
        COUNT(CASE WHEN status = 'finished' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(*), 0), 1
    )::text || '%'
FROM master_jobimage;
```

### Real-time system status
```sql
SELECT 
    'Active Users' as metric,
    COUNT(CASE WHEN is_active = true THEN 1 END)::text as value
FROM master_customuser
UNION ALL
SELECT 
    'Jobs In Progress',
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END)::text
FROM master_jobprofile
UNION ALL
SELECT 
    'Images Pending',
    COUNT(CASE WHEN status = 'unannotated' THEN 1 END)::text
FROM master_jobimage
UNION ALL
SELECT 
    'Current Issues',
    COUNT(CASE WHEN status = 'Issue' THEN 1 END)::text
FROM master_jobimage;
```

## 📋 **TROUBLESHOOTING QUERIES**

### Check for orphaned records
```sql
-- Images without jobs
SELECT COUNT(*) as orphaned_images
FROM master_jobimage ji
LEFT JOIN master_jobprofile jp ON ji.job_id = jp.id
WHERE jp.id IS NULL;
```

### Find users without assignments
```sql
SELECT 
    email,
    role,
    date_joined
FROM master_customuser 
WHERE role IN ('annotator', 'reviewer')
AND id NOT IN (
    SELECT COALESCE(worker_annotator_id, 0) FROM master_jobprofile
    UNION
    SELECT COALESCE(worker_reviewer_id, 0) FROM master_jobprofile
)
ORDER BY date_joined DESC;
```

## 💡 **Tips untuk Presentasi:**

### 🎯 **Urutan Presentasi yang Disarankan:**
1. **Database Overview** - Tunjukkan struktur tables
2. **User Management** - Show user roles dan activity
3. **Job Management** - Demonstrate workflow
4. **Image Processing** - Show annotation progress
5. **Performance Analytics** - Display productivity metrics
6. **System Monitoring** - Real-time status

### 🛠️ **Best Practices:**
- Gunakan `LIMIT 5-10` untuk demo supaya hasil tidak terlalu panjang
- Explain ERD structure sambil tunjukkan tables di pgAdmin
- Show real-time monitoring capabilities
- Highlight scalability advantages dari PostgreSQL vs SQLite

### 🚨 **Backup Commands kalau ada error:**
```sql
-- Reset query jika stuck
SELECT version();

-- Simple connectivity test
SELECT NOW() as current_time;

-- Check database connection
SELECT current_database(), current_user;
```

## 🎯 **Demo Script untuk Presentasi:**

1. **Opening:** "Mari kita lihat database PostgreSQL yang mendukung sistem anotasi image kita..."

2. **Show Tables:** Jalankan query database overview untuk tunjukkan struktur

3. **User Demo:** Tunjukkan user management dengan role-based access

4. **Workflow Demo:** Demonstrate job creation dan assignment process

5. **Progress Tracking:** Show real-time analytics dan monitoring

6. **Closing:** "Dengan PostgreSQL, kita bisa handle ribuan images dan multiple users secara concurrent..."

---

**Database Info:**
- **Database Name:** `anotasi_image_db`
- **Host:** `localhost:5432`
- **User:** `adrianhalim`
- **Schema:** `public`

**Good luck untuk presentasi besok! 🎯✨**
