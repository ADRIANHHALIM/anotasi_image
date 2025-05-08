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
def issue_solving_view(request):
    return render(request, "master/issue_solving.html")

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
        
        # Get actual counts from JobImage
        unannotated_count = JobImage.objects.filter(job=job, status='unannotated').count()
        in_review_count = JobImage.objects.filter(job=job, status='in_review').count()
        in_rework_count = JobImage.objects.filter(job=job, status='in_rework').count()
        finished_count = JobImage.objects.filter(job=job, status='finished').count()
        issues_count = JobImage.objects.filter(job=job, status='has_issues').count()
        total_count = JobImage.objects.filter(job=job).count()

        data = {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'image_count': total_count,
            'segmentation_type': job.segmentation_type,
            'shape_type': job.shape_type,
            'color': job.color,
            'start_date': job.start_date.strftime('%d/%m/%Y') if job.start_date else None,
            'end_date': job.end_date.strftime('%d/%m/%Y') if job.end_date else None,
            'status': job.status,
            'worker_annotator': job.worker_annotator if hasattr(job, 'worker_annotator') else None,
            'worker_reviewer': job.worker_reviewer if hasattr(job, 'worker_reviewer') else None,
            'unannotated_count': unannotated_count,
            'in_review_count': in_review_count,
            'in_rework_count': in_rework_count,
            'finished_count': finished_count,
            'issues_count': issues_count
        }
        return JsonResponse(data)
    except Exception as e:
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
