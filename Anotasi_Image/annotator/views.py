from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from functools import wraps
from master.models import JobProfile, JobImage, Notification, Issue
from django.utils import timezone
from django.db.models import Count, Q
import json

# Create your views here.

def annotator_required(view_func):
    """
    Custom decorator that requires user to be logged in and have annotator role
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/annotator/signin/')
        if request.user.role != 'annotator':
            messages.error(request, 'Access denied. This portal is for annotators only.')
            return redirect('/annotator/signin/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@csrf_protect
def signin_view(request):
    """
    Sign in view for annotators only
    """
    if request.user.is_authenticated:
        # Check if user is annotator
        if request.user.role == 'annotator':
            return redirect('annotator:annotate')
        else:
            # User is logged in but not annotator - redirect them to logout
            logout(request)
            messages.error(request, 'Access denied. This portal is for annotators only. You have been logged out.')
            return render(request, 'annotator/signin.html')
    
    if request.method == 'POST':
        email = request.POST.get('username')  # Form field name is username but we treat it as email
        password = request.POST.get('password')
        
        # Try to authenticate using email as username (CustomUser uses email as USERNAME_FIELD)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user is an annotator
            if user.role == 'annotator':
                login(request, user)
                messages.success(request, f'See you again, {user.username}!')
                
                # Redirect to next page or default to annotate
                next_url = request.GET.get('next', '/annotator/annotate/')
                return redirect(next_url)
            else:
                messages.error(request, 'Access denied. This portal is for annotators only.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'annotator/signin.html')

@annotator_required
def annotate_view(request):
    """
    View for the main annotation page - shows jobs assigned to current annotator
    """
    # Get jobs assigned to current annotator
    jobs = JobProfile.objects.filter(worker_annotator=request.user).annotate(
        total_images=Count('images'),
        completed_images=Count('images', filter=Q(images__status='annotated'))
    ).order_by('-date_created')
    
    # Calculate completion percentage for each job
    for job in jobs:
        if job.total_images > 0:
            job.completion_percentage = round((job.completed_images / job.total_images) * 100)
        else:
            job.completion_percentage = 0
    
    context = {
        'current_page': 'annotate',
        'user': request.user,
        'jobs': jobs,
    }
    return render(request, 'annotator/annotate.html', context)

@annotator_required
def notifications_view(request):
    """
    View for the notifications page
    """
    # Debug: Get current user explicitly
    current_user = request.user
    print(f"DEBUG: Current user = {current_user.username} (ID: {current_user.id})")
    
    # Get all notifications for current user, ordered by newest first
    notifications = Notification.objects.filter(
        recipient=current_user
    ).select_related('sender', 'job', 'issue').order_by('-created_at')
    
    print(f"DEBUG: Query result count = {notifications.count()}")
    
    # Also try direct ID query
    notifications_by_id = Notification.objects.filter(recipient_id=current_user.id)
    print(f"DEBUG: Direct ID query count = {notifications_by_id.count()}")
    
    context = {
        'current_page': 'notifications',
        'user': request.user,
        'notifications': notifications,
    }
    return render(request, 'annotator/notifications.html', context)

@annotator_required
def job_detail_view(request, job_id):
    """
    View for displaying the details of a specific job, including images and their status
    """
    # Get the job and make sure it's assigned to current user
    job = get_object_or_404(JobProfile, id=job_id, worker_annotator=request.user)
    
    # Get all images for this job
    all_images = job.images.all().order_by('id')
    
    # Get current tab and status filter
    current_tab = request.GET.get('tab', 'data')
    current_status = request.GET.get('status', '')
    issue_filter = request.GET.get('issue_status', 'all')
    
    # Filter images based on status if provided
    if current_status and current_status in ['unannotated', 'in_progress', 'in_review', 'in_rework', 'annotated', 'finished']:
        images = all_images.filter(status=current_status)
    else:
        images = all_images
    
    # Calculate status counts (always use all images for counts)
    status_counts = {
        'unannotated': all_images.filter(status='unannotated').count(),
        'in_progress': all_images.filter(status='in_progress').count(),
        'in_review': all_images.filter(status='in_review').count(),
        'in_rework': all_images.filter(status='in_rework').count(),
        'annotated': all_images.filter(status='annotated').count(),
        'finished': all_images.filter(status='finished').count(),
    }
    
    # Handle Issues data - using real Issue model
    # Get all issues for this job assigned to current user
    # Issues are only created by Master and Reviewer, not auto-generated
    all_issues = Issue.objects.filter(job=job, assigned_to=request.user).select_related('created_by', 'image')
    
    # Filter issues based on status
    if issue_filter == 'open':
        issues = all_issues.filter(status='open')
    elif issue_filter == 'eskalasi':
        issues = all_issues.filter(status='eskalasi')
    elif issue_filter == 'reworking':
        issues = all_issues.filter(status='reworking')
    elif issue_filter == 'closed':
        issues = all_issues.filter(status='closed')
    else:
        issues = all_issues
    
    # Calculate issue counts
    issue_counts = {
        'open': all_issues.filter(status='open').count(),
        'eskalasi': all_issues.filter(status='eskalasi').count(),
        'reworking': all_issues.filter(status='reworking').count(),
        'closed': all_issues.filter(status='closed').count(),
    }

    context = {
        'current_page': 'annotate',
        'user': request.user,
        'job': job,
        'images': images,
        'all_images': all_images,
        'status_counts': status_counts,
        'current_tab': current_tab,
        'current_status': current_status,
        'issues': issues,
        'issue_counts': issue_counts,
        'issue_filter': issue_filter,
    }
    return render(request, 'annotator/job_detail.html', context)

def signout_view(request):
    """
    Sign out view for annotators
    """
    logout(request)
    messages.success(request, 'You have been signed out successfully.')
    return redirect('annotator:signin')

def accept_notification_view(request, notification_id):
    """
    Accept notification and update status to 'accepted'
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)
        
    try:
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        # Update notification status to accepted
        notification.status = 'accepted'
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification accepted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
