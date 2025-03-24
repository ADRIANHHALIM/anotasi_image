from django.shortcuts import render, redirect
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
from .tokens import account_activation_token
from .models import CustomUser
from .forms import SignUpForm

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
    users = CustomUser.objects.all()
    return render(request, 'master/home.html', {'users': users})

@login_required
def assign_roles_view(request):
    new_members = CustomUser.objects.filter(role='guest')
    members = CustomUser.objects.exclude(role='guest')
    return render(request, "master/assign_roles.html", {'new_members': new_members, 'members': members})

login_required
def update_role(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            new_role = data.get('new_role')
            
            user = CustomUser.objects.get(id=user_id)
            user.role = new_role
            user.save()
            
            print(f"Updated user {user.email} role to {new_role}")  # Debug log
            
            return JsonResponse({'status': 'success'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def job_settings_view(request):
    return render(request, "master/job_settings.html")

@login_required
def issue_solving_view(request):
    return render(request, "master/issue_solving.html")

@login_required
def performance_view(request):
    return render(request, "master/performance.html")

@login_required
def process_validation_view(request):
    return render(request, "master/process_validations.html")