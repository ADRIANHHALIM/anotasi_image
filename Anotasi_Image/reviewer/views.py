from django.shortcuts import render, redirect, get_object_or_404
import base64
from PIL import Image
import os
from datetime import datetime, time
from django.utils import timezone
from django.templatetags.static import static
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password,check_password
from django.contrib import messages
from functools import wraps
from master.models import CustomUser, JobProfile, JobImage, Annotation, Segmentation, Issue
from .forms import LoginForm  # Only login form needed - signup handled by master app
import re
import json

# Create your views here.
def reviewer_required(view_func):
    """
    Custom decorator that requires user to be logged in and have reviewer or master role
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('reviewer:login')
        if request.user.role not in ['reviewer', 'master']:
            messages.error(request, f'Access denied. You are logged in as {request.user.role}. This portal is for reviewers only.')
            # Redirect to appropriate portal instead of forcing login
            if request.user.role == 'annotator':
                return redirect('/annotator/annotate/')
            elif request.user.role == 'master':
                return redirect('/')
            elif request.user.role == 'guest':
                messages.error(request, 'Akun Anda masih dalam status guest. Silakan tunggu admin untuk memberikan akses.')
                return redirect('/login/')
            else:
                # Only redirect to login if user role is unknown/invalid
                return redirect('reviewer:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def reviewer_required(view_func):
    """
    Custom decorator that requires user to be logged in and have reviewer or master role
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('reviewer:login')
        if request.user.role not in ['reviewer', 'master']:
            messages.error(request, f'Access denied. You are logged in as {request.user.role}. This portal is for reviewers only.')
            # Redirect to appropriate portal instead of forcing login
            if request.user.role == 'annotator':
                return redirect('/annotator/annotate/')
            elif request.user.role == 'master':
                return redirect('/')
            elif request.user.role == 'guest':
                messages.error(request, 'Akun Anda masih dalam status guest. Silakan tunggu admin untuk memberikan akses.')
                return redirect('/login/')
            else:
                # Only redirect to login if user role is unknown/invalid
                return redirect('reviewer:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_base64_images():
    logo_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/logo-trisakti.png")
    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        logo_base64 = f"data:image/png;base64,{encoded_string}"

    logo_search_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/logo-search.png")
    with open(logo_search_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        logo_search_base64 = f"data:image/png;base64,{encoded_string}"
    
    nav_reviewer_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/nav-reviewer.png")
    with open(nav_reviewer_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        nav_reviewer_base64 = f"data:image/png;base64,{encoded_string}"
    
    nav_isu_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/nav-isu.png")
    with open(nav_isu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        nav_isu_base64 = f"data:image/png;base64,{encoded_string}"
    
    nav_proses_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/nav-proses.png")
    with open(nav_proses_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        nav_proses_base64 = f"data:image/png;base64,{encoded_string}"

    nav_notif_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/nav-notif.png")
    with open(nav_notif_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        nav_notif_base64 = f"data:image/png;base64,{encoded_string}"
    
    nav_username_path = os.path.join(settings.BASE_DIR,"reviewer/static/reviewer/image/nav-username.png")
    with open(nav_username_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        nav_username_base64 = f"data:image/png;base64,{encoded_string}"
    context={
        "logo_base64": logo_base64,
        "logo_search_base64":logo_search_base64,
        "nav_reviewer_base64" : nav_reviewer_base64,
        "nav_isu_base64":nav_isu_base64,
        "nav_proses_base64":nav_proses_base64,
        "nav_notif_base64":nav_notif_base64,
        "nav_username_base64":nav_username_base64,
    }

    return (context)
@reviewer_required
def home_reviewer(request):
    user = request.user
        
    username = user.username
    number_email = user.email or user.phone_number or ''
    user_id = user.id

    list_ProfileJob = JobProfile.objects.filter(worker_reviewer=user_id)
    
    # Debug: print the profiles found
    print(f"DEBUG: Found {list_ProfileJob.count()} profiles for user {user_id}")
    for profile in list_ProfileJob:
        print(f"DEBUG: Profile ID={profile.id}, Title='{profile.title}', End Date={profile.end_date}")
    
    tasks = []
    now = timezone.localtime()   # sekarang di timezone aplikasi

    for profile in list_ProfileJob:
        # hitung deadline = end_date pukul 23:59:59
        deadline = datetime.combine(profile.end_date, time.max)
        deadline = timezone.make_aware(deadline, now.tzinfo)

        delta = deadline - now
        total_seconds = int(delta.total_seconds())

        if total_seconds <= 0:
            tr = "Times Up"
        else:
            hours, rem = divmod(total_seconds, 3600)
            if hours > 0:
                tr = f"{hours} hours left"
            else:
                minutes, seconds = divmod(rem, 60)
                if minutes > 0:
                    tr = f"{minutes} minutes left"
                else:
                    tr = f"less than 1 minute"

        # Get job images count for this profile
        job_images_count = JobImage.objects.filter(job=profile).count()

        tasks.append({
            'profile': profile,
            'job_images_count': job_images_count,
            'time_remaining': tr
        })

    context={
        'username':username,
        'number_email': number_email,
        'tasks': tasks,
        **get_base64_images(),
        
    }

    # Kirim data Base64 ke template
    return render(request, "reviewer/home_reviewer.html", context)

@reviewer_required
def task_review(request, id):
    user = request.user

    username = user.username
    number_email = user.email or user.phone_number or ''
    user_id = user.id

    # ✅ Ambil profile dan pastikan milik user
    profile = get_object_or_404(JobProfile, id=id, worker_reviewer=user_id)

    # Ambil data job terkait profile - remove select_related for image field since it's ImageField not ForeignKey
    data_job = JobImage.objects.filter(job=profile).select_related('job', 'annotator')
    total_images = data_job.count()

    context = {
        'profile_id': profile.id,
        'total_images': total_images,
        'data_job': data_job,
        'username': username,
        'number_email': number_email,
        **get_base64_images(),
    }
    return render(request, 'reviewer/task_review.html', context)


@reviewer_required
def isu(request):
    user = request.user
    username = user.username
    number_email = user.email or user.phone_number or ''
    
    context = {
        'username': username,
        'number_email': number_email,
        **get_base64_images(),
    }
    return render(request, 'reviewer/isu.html', context)
@csrf_protect
@csrf_protect
@csrf_protect
def login(request):
    print(f"Login view called - Method: {request.method}")
    print(f"CSRF token in META: {request.META.get('CSRF_COOKIE')}")
    print(f"CSRF token in POST: {request.POST.get('csrfmiddlewaretoken')}")
    
    if request.user.is_authenticated:
        # Check if user is reviewer or master
        if request.user.role in ['reviewer', 'master']:
            return redirect('reviewer:home_reviewer')
        else:
            # User is logged in but not reviewer - show warning
            messages.warning(request, f'You are currently logged in as {request.user.role}. To use the reviewer portal, please logout first and login with a reviewer account.')
            # Don't redirect - show the login form with warning
            
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = LoginForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            
        if form.is_valid():
            email = form.cleaned_data['email']  # Now correctly using email field
            password = form.cleaned_data['password']
            print(f"Attempting login with email: {email}")

            # Use Django's authentication system with email
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                print(f"User authenticated: {user.username}, role: {user.role}")
                # Check if user has reviewer or master role
                if user.role in ['reviewer', 'master']:
                    auth_login(request, user)
                    return redirect('reviewer:home_reviewer')
                else:
                    form.add_error(None, 'Access denied. This portal is for reviewers only.')
            else:
                print("Authentication failed")
                form.add_error(None, 'Invalid email or password.')
                
        context = {   
            'form': form,
            **get_base64_images(),
        }
        return render(request, 'reviewer/login.html', context)
    else:
        form = LoginForm()
        context = {
            'form': form,
            **get_base64_images(),
        }
        return render(request, 'reviewer/login.html', context)

    
@reviewer_required
def isu_anotasi(request, index=0):
    user = request.user
    profile_id_raw = request.GET.get('profile_id') or request.session.get('profile_id')
    try:
        profile_id = int(profile_id_raw)
    except (TypeError, ValueError):
        return redirect('reviewer:home_reviewer')

    profile = JobProfile.objects.filter(id=profile_id, worker_reviewer=user.id).first()
    if not profile:
        return redirect('reviewer:home_reviewer')

    job_images = (
        JobImage.objects
        .filter(job_id=profile_id)
        .select_related('job')
        .order_by('id')
    )
    total = job_images.count()
    if total == 0:
        return render(request, 'reviewer/tidak_ada_gambar.html')
    if index < 0 or index >= total:
        return redirect('reviewer:isu_anotasi', index=0)

    # ✅ Ambil ukuran semua gambar
    image_sizes = []
    for img in job_images:
        try:
            path = img.image.path
            with Image.open(path) as im:
                width, height = im.size
                image_sizes.append({'width': width, 'height': height})
        except Exception as e:
            image_sizes.append({'width': 0, 'height': 0})  # fallback jika gagal

    # Gambar yang sedang ditampilkan
    job_image = job_images[index]
    gambar = job_image.image
    current_image_size = image_sizes[index]
    job_profile = job_image.job.id

    # Ambil data segmentasi & anotasi
    segmentasi_list = Segmentation.objects.filter(job=job_image)
    anotasi_list = Annotation.objects.filter(job_image=job_image)

    anotasi_semantic = anotasi_list.filter(segmentation__segmentation_type__name='semantic')
    anotasi_instance = anotasi_list.filter(segmentation__segmentation_type__name='instance')
    anotasi_panoptic = anotasi_list.filter(segmentation__segmentation_type__name='panoptic')

    polygon_semantic_list = [
        {
            'warna': a.segmentation.color,
            'label': a.segmentation.label,
            'points': " ".join(f"{p.x_coordinate},{p.y_coordinate}" for p in a.polygon_points.all().order_by('order'))
        }
        for a in anotasi_semantic if a.polygon_points.exists()
    ]

    polygon_panoptic_list = [
        {
            'warna': a.segmentation.color,
            'label': a.segmentation.label,
            'points': " ".join(f"{p.x_coordinate},{p.y_coordinate}" for p in a.polygon_points.all().order_by('order'))
        }
        for a in anotasi_panoptic if a.polygon_points.exists()
    ]
    segmentasi_anotasi_info = []

    for segmentasi in segmentasi_list:
        anotasi_terkait = anotasi_list.filter(segmentation=segmentasi)
        anotasi_items = []
        for i, anotasi in enumerate(anotasi_terkait, start=1):
            anotasi_items.append({
                'anotasi_id': anotasi.id,
                'nama': f"{segmentasi.label} {i}",
                'warna': segmentasi.color,
                'label': segmentasi.label,
                'tipe': segmentasi.segmentation_type.name.title(),  # Instance / Semantic / Panoptic
            })
        if anotasi_items:
            segmentasi_anotasi_info.extend(anotasi_items)
    # Calculate status counts for all job images
    pending_count = job_images.filter(status='pending').count()
    in_progress_count = job_images.filter(status='in_progress').count()
    annotated_count = job_images.filter(status='annotated').count()
    reviewed_count = job_images.filter(status='reviewed').count()
    unannotated_count = job_images.filter(status='unannotated').count()
    in_review_count = job_images.filter(status='in_review').count()
    in_rework_count = job_images.filter(status='in_rework').count()
    finished_count = job_images.filter(status='finished').count()
    
    # Count issues (assuming there's an Issue model related to JobImage)
    issues_count = Issue.objects.filter(image__job_id=profile_id).count()
    
    # Prepare annotation data for JSON (similar to annotator views)
    annotation_data = []
    for ann in anotasi_list:
        if hasattr(ann, 'x_min') and hasattr(ann, 'y_min') and hasattr(ann, 'x_max') and hasattr(ann, 'y_max'):
            annotation_data.append({
                'label': ann.segmentation.label if ann.segmentation else 'Unknown',
                'bbox': [ann.x_min, ann.y_min, ann.x_max, ann.y_max],
                'is_auto_generated': getattr(ann, 'is_auto_generated', False)
            })
    print(f"DEBUG: Annotation data prepared for reviewer: {annotation_data}")
    
    print("JobImage ID:", job_image.id)
    print("Segmentasi count:", segmentasi_list.count())
    print("Anotasi count:", anotasi_list.count())
    print("Semantic annotations:", anotasi_semantic.count())
    print("Panoptic annotations:", anotasi_panoptic.count())  
    context = {
        'username': user.username,
        'number_email': user.email or getattr(user, 'phone_number', '') or '',
        'profile_id': profile_id,
        'nama_profile_job': profile.title,
        'filename': gambar.name,
        'gambar': gambar,
        'gambar_id': job_image.id,
        'image_index': index + 1,
        'total_images': total,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'annotated_count': annotated_count,
        'reviewed_count': reviewed_count,
        'unannotated_count': unannotated_count,
        'in_review_count': in_review_count,
        'in_rework_count': in_rework_count,
        'finished_count': finished_count,
        'issues_count': issues_count,
        'segmentasi_list': segmentasi_list,
        'anotasi_list': anotasi_list,
        'anotasi_box': anotasi_instance,
        'lebar_gambar': current_image_size['width'],    # ✅ width gambar sekarang
        'tinggi_gambar': current_image_size['height'],  # ✅ height gambar sekarang
        'image_sizes': image_sizes,                     # ✅ semua ukuran gambar
        'polygon_semantic_list': polygon_semantic_list,
        'polygon_panoptic_list': polygon_panoptic_list,
        'total_semantic': anotasi_semantic.count(),
        'total_instance': anotasi_instance.count(),
        'total_panoptic': anotasi_panoptic.count(),
        'segmentasi_anotasi_info': segmentasi_anotasi_info,
        'annotations_json': json.dumps(annotation_data),  # Add JSON data for bounding box rendering
        **get_base64_images(),
    }
    return render(request, 'reviewer/isu_anotasi.html', context)

@reviewer_required
def isu_image(request):
    user = request.user
    username = user.username
    number_email = user.email or user.phone_number or ''
    
    context = {
        'username': username,
        'number_email': number_email,
        **get_base64_images()
    }
    return render(request, 'reviewer/isu_image.html', context)

@csrf_protect
@reviewer_required
def finish_review_view(request, image_id):
    """
    Mark review as finished and notify master
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    try:
        image_obj = get_object_or_404(JobImage, id=image_id)
        
        # Check if user is the assigned reviewer for this job
        if image_obj.job.worker_reviewer != request.user:
            return JsonResponse({'success': False, 'error': 'You are not assigned to this job'}, status=403)
        
        # Update status to 'finished' (completed review)
        image_obj.status = 'finished'
        image_obj.review_time = timezone.now()
        image_obj.save()
        
        # Check if all images in the job are finished
        job_profile = image_obj.job
        total_images = JobImage.objects.filter(job=job_profile).count()
        finished_images = JobImage.objects.filter(job=job_profile, status='finished').count()
        
        # If all images are finished, update job status to 'finish' (matching JobProfile model)
        if total_images == finished_images:
            job_profile.status = 'finish'  # Changed from 'completed' to 'finish' to match JobProfile model
            job_profile.save()
            
            # TODO: Create notification for master
            # if job_profile.created_by:  # Assuming master is the creator
            #     Notification.objects.create(
            #         recipient=job_profile.created_by,
            #         message=f"Job '{job_profile.title}' has been completed",
            #         notification_type='job_completed'
            #     )
        
        return JsonResponse({
            'success': True, 
            'message': 'Review marked as finished',
            'job_completed': total_images == finished_images
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def logout(request):
    """Logout view for reviewers"""
    auth_logout(request)
    return redirect('reviewer:login')
