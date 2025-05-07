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
from .models import CustomUser, Dataset, JobProfile
from .forms import SignUpForm
import os
from django.core.files.storage import FileSystemStorage

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
        job = JobProfile.objects.get(id=job_id)
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'worker_annotator': job.worker_annotator,
            'worker_reviewer': job.worker_reviewer,
            'segmentation_type': job.segmentation_type,
            'shape_type': job.shape_type,
            'color': job.color,
            'start_date': job.start_date.strftime('%d %B %Y'),
            'end_date': job.end_date.strftime('%d %B %Y'),
            'image_count': job.image_count,
            'status': job.status,
        })
    except JobProfile.DoesNotExist:
        return JsonResponse({'error': 'Job profile not found'}, status=404)

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