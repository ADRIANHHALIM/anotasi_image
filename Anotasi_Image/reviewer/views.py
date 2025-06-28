from django.shortcuts import render, redirect, get_object_or_404
import base64
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
            messages.error(request, 'Access denied. Reviewer access required.')
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

    # Ambil data job terkait profile
    data_job = JobImage.objects.filter(job=profile).select_related('image')
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
def login(request):
    if request.user.is_authenticated:
        # Check if user is reviewer or master
        if request.user.role in ['reviewer', 'master']:
            return redirect('reviewer:home_reviewer')
        else:
            # User is logged in but not reviewer - redirect them to logout
            auth_logout(request)
            messages.error(request, 'Access denied. This portal is for reviewers only. You have been logged out.')
            
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # Form field is named username but we treat it as email
            password = form.cleaned_data['password']

            # Use Django's authentication system with email
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                # Check if user has reviewer or master role
                if user.role in ['reviewer', 'master']:
                    auth_login(request, user)
                    return redirect('reviewer:home_reviewer')
                else:
                    form.add_error(None, 'Access denied. This portal is for reviewers only.')
            else:
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
def isu_anotasi(request, index):
    user = request.user
    user_id = user.id
    # Get profile_id from session or URL parameter - you may need to adjust this
    profile_id = request.GET.get('profile_id') or request.session.get('profile_id')
    
    if not profile_id:
        return redirect('reviewer:home_reviewer')

    # ✅ Validasi bahwa profile_id benar-benar milik user yang login
    profile = JobProfile.objects.filter(id=profile_id, worker_reviewer=user_id).first()
    if not profile:
        return redirect('reviewer:home_reviewer')  # atau tampilkan pesan error

    nama_profile_job = profile.title

    # ✅ Ambil JobImage hanya untuk profile ini
    job_items = JobImage.objects.select_related('image').filter(
        job=profile_id
    ).order_by('id')

    if index < 0 or index >= job_items.count():
        return redirect('reviewer:isu_anotasi', index=0)  # fallback ke index awal

    job_item = job_items[index]
    gambar = job_item.image

    segmentasi_list = Segmentation.objects.filter(job_image=job_item)
    anotasi_list = Annotation.objects.filter(job_image=job_item)

    # === Basic annotation data (simplified for new model structure) ===
    # Note: This needs to be updated to work with the new annotation models
    segmentasi_list = Segmentation.objects.filter(job=job_item.job)
    anotasi_list = Annotation.objects.filter(job_image=job_item)

    # === Semantic (simplified) ===
    anotasi_semantic = Annotation.objects.filter(
        job_image=job_item,
        segmentation__segmentation_type__name='Semantic'
    )
    polygon_semantic_list = []
    for anotasi in anotasi_semantic:
        # Get polygon points for this annotation
        points = anotasi.polygon_points.all().order_by('order')
        if points:
            polygon_semantic_list.append({
                'warna': anotasi.segmentation.color if anotasi.segmentation else '#000000',
                'label': anotasi.segmentation.label if anotasi.segmentation else 'Unknown',
                'points': " ".join([f"{point.x_coordinate},{point.y_coordinate}" for point in points]),
            })

    # === Instance (simplified) ===
    anotasi_instance = Annotation.objects.filter(
        job_image=job_item,
        segmentation__segmentation_type__name='Instance'
    )

    # === Panoptic (simplified) ===
    anotasi_panoptic = Annotation.objects.filter(
        job_image=job_item,
        segmentation__segmentation_type__name='Panoptic'
    )
    polygon_panoptic_list = []
    for anotasi in anotasi_panoptic:
        # Get polygon points for this annotation
        points = anotasi.polygon_points.all().order_by('order')
        if points:
            polygon_panoptic_list.append({
                'warna': anotasi.segmentation.color if anotasi.segmentation else '#000000',
                'label': anotasi.segmentation.label if anotasi.segmentation else 'Unknown',
                'points': " ".join([f"{point.x_coordinate},{point.y_coordinate}" for point in points]),
            })

    context = {
        'username': user.username,
        'number_email': user.email or user.phone_number or '',
        'profile_id': profile_id,
        'nama_profile_job': nama_profile_job,
        'filename': gambar.name if hasattr(gambar, 'name') else 'image.jpg',
        'gambar_id': gambar.id if hasattr(gambar, 'id') else job_item.id,
        'image_index': index + 1,
        'total_images': job_items.count(),
        'segmentasi_list': segmentasi_list,
        'anotasi_list': anotasi_list,
        'anotasi_box': anotasi_instance,
        'lebar_gambar': 800,  # Default width - update if image dimensions are available
        'tinggi_gambar': 600,  # Default height - update if image dimensions are available
        'polygon_semantic_list': polygon_semantic_list,
        'polygon_panoptic_list': polygon_panoptic_list,
        'total_semantic': anotasi_semantic.count(),
        'total_instance': anotasi_instance.count(),
        'total_panoptic': anotasi_panoptic.count(),
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

def logout(request):
    """Logout view for reviewers"""
    auth_logout(request)
    return redirect('reviewer:login')
