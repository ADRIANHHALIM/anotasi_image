from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login setelah berhasil daftar
            return redirect('home')  # Ganti dengan halaman utama (pastikan 'home' ada di urls.py)
    else:
        form = SignUpForm()

    return render(request, "master/signup.html", {"form": form})

def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")  # Gunakan .get() untuk menghindari KeyError
        password = request.POST.get("password")
        
        if username and password:  # Cek jika username & password dikirim
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')  # Ganti dengan halaman utama
            else:
                error_message = "Username atau Password salah!"
        else:
            error_message = "Harap isi Username dan Password!"

    return render(request, "master/login.html", {"error_message": error_message})

def logout_view(request):
    logout(request)
    return redirect('login')  # Kembali ke halaman login setelah logout

@login_required  # Pastikan hanya user yang login bisa mengakses halaman ini
def create_view(request):
    return render(request, 'master/create.html')
