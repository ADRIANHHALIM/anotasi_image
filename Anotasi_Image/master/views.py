from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from .tokens import account_activation_token
from .models import CustomUser

from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        errors = {}

        if CustomUser.objects.filter(username=username).exists():
            errors["username"] = "Username sudah digunakan!"

        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.is_active:
                errors["email"] = "Email sudah terdaftar tetapi belum diverifikasi! Silakan cek email Anda."
            else:
                errors["email"] = "Email sudah digunakan dan sudah terverifikasi!"

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            errors["phone_number"] = "Nomor HP sudah digunakan!"

        if password1 != password2:
            errors["password"] = "Konfirmasi password tidak cocok!"

        if errors:
            return render(request, "master/signup.html", {"errors": errors})

        user = CustomUser.objects.create_user(
            username=username, first_name=first_name, last_name=last_name,
            email=email, phone_number=phone_number, password=password1
        )
        user.is_active = False  # Tunggu verifikasi email
        user.save()

        current_site = get_current_site(request)
        subject = "Aktivasi Akun Anda"
        message_html = render_to_string(
            "master/activation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        message_plain = strip_tags(message_html)  # Konversi HTML ke teks biasa

        send_mail(subject, message_plain, "your-email@gmail.com", [email], html_message=message_html)

        return render(request, "master/activation_pending.html")

    return render(request, "master/signup.html")

User = get_user_model()
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])  # Simpan perubahan

        # Pastikan Django mengetahui backend yang digunakan
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user, backend=user.backend)

        messages.success(request, "Akun berhasil diaktifkan! Silakan login.")
        return redirect("home")

    else:
        messages.error(request, "Link aktivasi tidak valid atau sudah kedaluwarsa.")
        return redirect("login")

@csrf_protect
def login_view(request):
    error_message = None
    if request.method == "POST":
        username_or_email = request.POST.get("username")  # Bisa email atau username
        password = request.POST.get("password")

        if username_or_email and password:
            user = authenticate(request, username=username_or_email, password=password)  # Bisa pakai email atau username
            if user:
                if user.is_active or user.is_staff:  # Allow login if user is active or staff
                    login(request, user)
                    return redirect("home")  # Redirect ke home
                else:
                    error_message = "Akun belum diaktifkan! Silakan cek email Anda untuk aktivasi."
            else:
                error_message = "Username/Email atau Password salah!"
        else:
            error_message = "Harap isi Username/Email dan Password!"

    return render(request, "master/login.html", {"error_message": error_message})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, "master/home.html")
