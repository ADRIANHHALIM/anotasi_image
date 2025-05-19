from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_backends
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from django.utils import timezone
import json
from .tokens import account_activation_token
from .models import CustomUser, Dataset, JobProfile, JobImage
from .forms import SignUpForm
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings  # Add this at the top with other imports
from .models import CustomUser, Dataset, JobProfile, JobImage  # Update your imports at the top

def signup_view(request):
    if request.method == "POST":
        print("POST data:", request.POST)  # Debug print
        # Create a form instance with the POST data
        data = {
            'username': request.POST.get('username'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'password1': request.POST.get('password1'),
            'password2': request.POST.get('password2'),
        }
        print("Form data:", data)
        form = SignUpForm(data)

        if form.is_valid():
            print("Form is valid")
            user = form.save()
            print("User saved:", user)
            # Authenticate user
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            if user:
                # login(request, user)
                messages.success(request, "Akun berhasil dibuat! Selamat datang!")
                return redirect("master:login")
            else:
                messages.error(request, "Gagal melakukan autentikasi")
        else:
            # Add form errors to messages
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()

    return render(request, "master/signup.html", {"form": form})

def login_view(request):
    error_message = None
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # First try to authenticate with email
        user = authenticate(request, email=username_or_email, password=password)
        if user is None:
            # If email auth fails, try with username
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login berhasil!")
                return redirect("master:home")
            else:
                error_message = "Akun belum diaktifkan!"
        else:
            error_message = "Username/Email atau Password salah!"
            messages.error(request, error_message)

    return render(request, "master/login.html", {"error_message": error_message})

def logout_view(request):
    logout(request)
    return redirect('master:login')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Akun berhasil diaktifkan! Silakan login.")
        return redirect("master:home")
    else:
        messages.error(request, "Link aktivasi tidak valid atau sudah kedaluwarsa.")
        return redirect("master:login")

@login_required
def home_view(request):
    context = {
        'users': CustomUser.objects.all(),
        'datasets': Dataset.objects.all().order_by('-date_created'),
        'status_list': [
            {'name': 'Andy Wirawan', 'status': 'Not Ready'},
        ]
    }
    return render(request, 'master/home.html', context)

@login_required
def assign_roles_view(request):
    new_members = CustomUser.objects.filter(role='guest')
    members = CustomUser.objects.exclude(role='guest')
    return render(request, "master/assign_roles.html", {'new_members': new_members, 'members': members})

@login_required
@require_http_methods(["POST"])
def update_role(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_role = data.get('new_role')

        if not user_id or not new_role:
            return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

        user = CustomUser.objects.get(id=user_id)
        user.role = new_role
        user.save()

        return JsonResponse({'status': 'success', 'message': 'Role updated successfully'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def job_settings_view(request):
    if request.method == 'POST':
        try:
            # Create new job profile
            job = JobProfile.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                segmentation_type=request.POST.get('segmentation'),
                shape_type=request.POST.get('shape'),
                color=request.POST.get('color'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date')
            )
            return JsonResponse({'status': 'success', 'message': 'Job profile created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    jobs = JobProfile.objects.all().order_by('-start_date')
    return render(request, "master/job_settings.html", {'jobs': jobs})

@login_required
def issue_detail_view(request, job_id):
    try:
        job = get_object_or_404(JobProfile, id=job_id)
        print("=== Debug Info ===")
        print(f"Job ID: {job_id}")
        print(f"Job Title: {job.title}")

        # Get all images for the job, not just those with issues
        job_images = JobImage.objects.filter(job=job)
        print(f"Total images found: {job_images.count()}")

        # Also log the count of images with issues for debugging
        issues_images_count = job_images.filter(status='Issue').count()
        print(f"Images with issues found: {issues_images_count}")

        # Add status counts to the response
        unannotated_count = JobImage.objects.filter(job=job, status='unannotated').count()
        in_review_count = JobImage.objects.filter(job=job, status='in_review').count()
        in_rework_count = JobImage.objects.filter(job=job, status='in_rework').count()
        finished_count = JobImage.objects.filter(job=job, status='finished').count()
        issues_count = JobImage.objects.filter(job=job, status='Issue').count()

        data = {
            'title': job.title,
            'unannotated_count': unannotated_count,
            'in_review_count': in_review_count,
            'in_rework_count': in_rework_count,
            'finished_count': finished_count,
            'issues_count': issues_count,
            'images': []
        }

        # Detailed logging for each image
        for img in job_images:
            if not img.image:
                print(f"Image ID {img.id}: No image file attached")
                continue

            try:
                # Verify image file exists
                image_exists = os.path.exists(img.image.path)
                print(f"Image ID: {img.id}")
                print(f"Image URL: {img.image.url}")
                print(f"Image Path: {img.image.path}")
                print(f"Image Exists: {image_exists}")

                if not image_exists:
                    print(f"WARNING: Image file does not exist at {img.image.path}")
                    continue

                # Build absolute URI for the image
                image_url = request.build_absolute_uri(img.image.url)
                print(f"Processing image ID {img.id}: {image_url}")

                # Add image data to response
                data['images'].append({
                    'url': image_url,
                    'annotator': img.annotator.email if img.annotator else 'Unassigned',
                    'issue_description': img.issue_description or 'No description'
                })
            except Exception as img_error:
                print(f"Error processing image ID {img.id}: {str(img_error)}")
                # Continue with next image instead of failing completely
                continue

        # Log the number of images being returned
        print(f"Returning {len(data['images'])} images")
        print("=== End Debug Info ===")

        return JsonResponse(data)
    except Exception as e:
        print(f"Error in issue_detail_view: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def performance_view(request):
    return render(request, "master/performance.html")

@login_required
def process_validation_view(request):
    return render(request, "master/process_validations.html")

@login_required
@require_http_methods(["POST"])
def add_dataset(request):
    try:
        name = request.POST.get('name')
        labeler_id = request.POST.get('labeler')
        dataset_file = request.FILES.get('dataset_file')

        if not all([name, labeler_id, dataset_file]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)

        # Handle file upload
        file_path = handle_dataset_upload(dataset_file)

        # Create dataset record
        dataset = Dataset.objects.create(
            name=name,
            labeler_id=labeler_id,
            file_path=file_path
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Dataset added successfully',
            'id': dataset.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def add_dataset_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            labeler_id = request.POST.get('labeler')
            dataset_file = request.FILES.get('dataset_file')

            if not all([name, labeler_id, dataset_file]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)

            # Save file
            fs = FileSystemStorage()
            filename = fs.save(f'datasets/{dataset_file.name}', dataset_file)
            file_path = fs.url(filename)

            # Create dataset
            dataset = Dataset.objects.create(
                name=name,
                labeler_id=labeler_id,
                file_path=file_path,
                count=0  # You can update this based on your needs
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Dataset added successfully',
                'id': dataset.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@login_required
@require_http_methods(["POST"])
def create_job_profile(request):
    try:
        job = JobProfile.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            segmentation_type=request.POST.get('segmentation'),
            shape_type=request.POST.get('shape'),
            color=request.POST.get('color'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date')
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Job profile created successfully',
            'id': job.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def job_profile_detail(request, job_id):
    try:
        job = get_object_or_404(JobProfile, id=job_id)
        print(f"Found job: {job.id}")  # Debug log

        data = {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'worker_annotator': job.worker_annotator.email if job.worker_annotator else None,
            'worker_reviewer': job.worker_reviewer.email if job.worker_reviewer else None,
            'segmentation_type': job.segmentation_type,
            'shape_type': job.shape_type,
            'color': job.color,
            'status': job.status,
            'start_date': job.start_date.strftime('%Y-%m-%d') if job.start_date else None,
            'end_date': job.end_date.strftime('%Y-%m-%d') if job.end_date else None,
            'first_image_url': job.get_first_image_url(),
            'image_count': JobImage.objects.filter(job=job).count(),
            'unannotated_count': JobImage.objects.filter(job=job, status='unannotated').count(),
            'in_review_count': JobImage.objects.filter(job=job, status='in_review').count(),
            'in_rework_count': JobImage.objects.filter(job=job, status='in_rework').count(),
            'finished_count': JobImage.objects.filter(job=job, status='finished').count(),
            'issues_count': JobImage.objects.filter(job=job, status='Issue').count(),
        }

        print(f"Returning data: {data}")  # Debug log
        return JsonResponse(data)

    except Exception as e:
        print(f"Error in job_profile_detail: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

# Daataset flow for edit and delete
@login_required
def edit_dataset_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)

    if request.method == 'POST':
        try:
            dataset.name = request.POST.get('name')
            dataset.labeler_id = request.POST.get('labeler')

            if 'dataset_file' in request.FILES:
                # Handle new file upload if provided
                dataset_file = request.FILES['dataset_file']
                fs = FileSystemStorage()
                filename = fs.save(f'datasets/{dataset_file.name}', dataset_file)
                dataset.file_path = fs.url(filename)

            dataset.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Dataset updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@login_required
def delete_dataset_view(request, dataset_id):
    if request.method == 'POST':
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            dataset.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Dataset deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@login_required
@require_http_methods(["POST"])
def upload_job_images(request):
    try:
        job_id = request.POST.get('job_id')
        job = JobProfile.objects.get(id=job_id)
        files = request.FILES.getlist('images[]')

        current_count = JobImage.objects.filter(job=job).count()
        if current_count + len(files) > 150:
            return JsonResponse({
                'status': 'error',
                'message': f'Cannot add {len(files)} images. Maximum limit is 150 images.'
            }, status=400)

        # Upload new images
        uploaded_count = 0
        for file in files:
            if file.content_type.startswith('image/'):
                JobImage.objects.create(
                    job=job,
                    image=file,
                    status='unannotated'  # Default status for new uploads
                )
                uploaded_count += 1

        # Get updated counts after upload
        new_total = JobImage.objects.filter(job=job).count()
        unannotated_count = JobImage.objects.filter(job=job, status='unannotated').count()
        in_review_count = JobImage.objects.filter(job=job, status='in_review').count()
        in_rework_count = JobImage.objects.filter(job=job, status='in_rework').count()
        finished_count = JobImage.objects.filter(job=job, status='finished').count()
        issues_count = JobImage.objects.filter(job=job, status='has_issues').count()

        # Update job status and image count
        if job.status == 'not_assign' and new_total > 0:
            job.status = 'in_progress'
        job.image_count = new_total
        job.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{uploaded_count} images uploaded successfully',
            'new_image_count': new_total,
            'new_status': job.status,
            'unannotated_count': unannotated_count,
            'in_review_count': in_review_count,
            'in_rework_count': in_rework_count,
            'finished_count': finished_count,
            'issues_count': issues_count
        })

    except JobProfile.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_workers(request, role):
    """Get list of available workers by role"""
    try:
        workers = CustomUser.objects.filter(role=role, is_active=True)
        return JsonResponse({
            'workers': [{
                'id': worker.id,
                'email': worker.email,
                'phone': worker.phone_number,  # Make sure this matches your model field
                'name': f"{worker.first_name} {worker.last_name}".strip()
            } for worker in workers]
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def assign_worker(request):
    """Assign worker to a job"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        worker_id = data.get('worker_id')
        role = data.get('role')

        job = JobProfile.objects.get(id=job_id)
        worker = CustomUser.objects.get(id=worker_id)

        if role == 'annotator':
            job.worker_annotator = worker
        elif role == 'reviewer':
            job.worker_reviewer = worker

        job.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{role.title()} assigned successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def assign_workers(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        annotator_id = data.get('annotator_id')
        reviewer_id = data.get('reviewer_id')

        if not all([job_id, annotator_id, reviewer_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)

        job = JobProfile.objects.get(id=job_id)
        annotator = CustomUser.objects.get(id=annotator_id)
        reviewer = CustomUser.objects.get(id=reviewer_id)

        # Update job with worker assignments
        job.worker_annotator = annotator
        job.worker_reviewer = reviewer
        job.status = 'in_progress'
        job.save()

        return JsonResponse({
            'status': 'success',
            'annotator_name': annotator.email,
            'reviewer_name': reviewer.email,
            'new_status': 'In Progress'  # Match dengan get_status_display()
        })
    except (JobProfile.DoesNotExist, CustomUser.DoesNotExist) as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Job or User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def home(request):
    # Dummy data untuk development UI
    context = {
        'assignment_stats': {
            'total': 16765,
            'assign': 300,
            'progress': 450,
            'reviewing': 200,
            'finished': 150
        },
        'datasets': [
            {
                'name': 'dataset_kendaraan',
                'labeler': 'Andy',
                'date': '17/04/2024',
                'count': 110
            }
            # More dummy data
        ],
        'status_list': [
            {'name': 'Andy Wirawan', 'status': 'Not Ready'},
            {'name': 'Wiyoko Suprapto', 'status': 'Ready'}
        ]
    }
    return render(request, 'master/home.html', context)

def handle_dataset_upload(dataset_file):
    """
    Handle the upload of dataset files
    Returns the file path where the dataset is stored
    """
    try:
        fs = FileSystemStorage()
        # Create datasets directory if it doesn't exist
        dataset_dir = os.path.join('datasets')
        os.makedirs(os.path.join(settings.MEDIA_ROOT, dataset_dir), exist_ok=True)

        # Save file
        filename = fs.save(f'datasets/{dataset_file.name}', dataset_file)
        file_path = fs.url(filename)
        return file_path
    except Exception as e:
        raise Exception(f"Error uploading dataset file: {str(e)}")

@login_required
def get_job_profile(request, job_id):
    try:
        job = JobProfile.objects.select_related('worker_annotator', 'worker_reviewer').get(id=job_id)

        # Debug logging
        print(f"Retrieved job: {job.id}, annotator: {job.worker_annotator}, reviewer: {job.worker_reviewer}")

        # Get worker information with improved error handling
        worker_annotator_email = '-'
        worker_annotator_name = '-'
        worker_reviewer_email = '-'
        worker_reviewer_name = '-'

        # Safely get annotator information
        if job.worker_annotator:
            try:
                worker_annotator_email = job.worker_annotator.email
                worker_annotator_name = f"{job.worker_annotator.first_name or ''} {job.worker_annotator.last_name or ''}".strip() or job.worker_annotator.email
            except Exception as e:
                print(f"Error accessing annotator info: {e}")

        # Safely get reviewer information
        if job.worker_reviewer:
            try:
                worker_reviewer_email = job.worker_reviewer.email
                worker_reviewer_name = f"{job.worker_reviewer.first_name or ''} {job.worker_reviewer.last_name or ''}".strip() or job.worker_reviewer.email
            except Exception as e:
                print(f"Error accessing reviewer info: {e}")

        # Get job image counts with error handling
        try:
            job_images = JobImage.objects.filter(job=job)
            image_counts = {
                'total': job_images.count(),
                'unannotated': job_images.filter(status='unannotated').count(),
                'in_review': job_images.filter(status='in_review').count(),
                'in_rework': job_images.filter(status='in_rework').count(),
                'finished': job_images.filter(status='finished').count(),
                'issues': job_images.filter(status='issues').count(),
            }
        except Exception as e:
            print(f"Error getting image counts: {e}")
            image_counts = {
                'total': 0, 'unannotated': 0, 'in_review': 0,
                'in_rework': 0, 'finished': 0, 'issues': 0
            }

        data = {
            'id': job.id,
            'title': job.title or '',
            'description': job.description or '',
            'hotkey': getattr(job, 'hotkey', '') or '',
            'worker_annotator': worker_annotator_email,
            'worker_reviewer': worker_reviewer_email,
            'worker_annotator_name': worker_annotator_name,
            'worker_reviewer_name': worker_reviewer_name,
            'segmentation_type': job.segmentation_type or '',
            'shape_type': job.shape_type or '',
            'color': job.color or '#000000',
            'status': job.get_status_display() or 'Not Assigned',
            'start_date': job.start_date.strftime('%Y-%m-%d') if job.start_date else None,
            'end_date': job.end_date.strftime('%Y-%m-%d') if job.end_date else None,
            'image_count': image_counts['total'],
            'unannotated_count': image_counts['unannotated'],
            'in_review_count': image_counts['in_review'],
            'in_rework_count': image_counts['in_rework'],
            'finished_count': image_counts['finished'],
            'issues_count': image_counts['issues'],
        }

        # Debug logging
        print("Sending response data:", data)
        return JsonResponse(data)

    except JobProfile.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        import traceback
        print("Error in get_job_profile:")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def issue_solving_view(request):
    """View for handling issue solving page"""
    try:
        # Get all jobs with their image counts and issues
        jobs = JobProfile.objects.all().order_by('-start_date')

        # Add additional data for each job
        for job in jobs:
            # Get total images count
            total_images = job.images.count()

            # Get finished images count
            finished_count = job.images.filter(status='finished').count()

            # Calculate progress percentage
            job.progress_percentage = int((finished_count / total_images * 100) if total_images > 0 else 0)

            # Get issues count
            job.issues_count = job.images.filter(status='Issue').count()

            # Get first image for display
            job.first_image_url = job.get_first_image_url()

        context = {
            'jobs': jobs,
            'current_date': timezone.now().strftime('%d %B %Y')
        }

        return render(request, 'master/Issue_solving.html', context)

    except Exception as e:
        print(f"Error in issue_solving_view: {e}")
        return render(request, 'master/Issue_solving.html', {
            'jobs': [],
            'current_date': timezone.now().strftime('%d %B %Y'),
            'error': str(e)
        })
