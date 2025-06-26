from django.shortcuts import render, redirect, get_object_or_404
import base64
import os
from datetime import datetime, time
from django.utils import timezone
from django.templatetags.static import static
from django.conf import settings
from django.http import JsonResponse
from .models import *
from .forms import *
import re
from django.contrib.auth.hashers import make_password,check_password

# Create your views here.

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
def home_reviewer(request):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')
    username = request.session.get('username')
    number_email = request.session.get('contact')
    user_id = request.session.get('user_id')  

    list_ProfileJob = ProfileJob.objects.filter(id_pengguna=user_id)
    
    list_JobItem    = JobItem.objects.filter()

    tasks = []
    now = timezone.localtime()   # sekarang di timezone aplikasi

    for profile, job in zip(list_ProfileJob, list_JobItem):
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

        tasks.append({
            'profile': profile,
            'job': job,
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

# def home_reviewer(request):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')

    username = request.session.get('username')
    number_email = request.session.get('contact')
    user_id = request.session.get('user_id')

    list_ProfileJob = ProfileJob.objects.filter(id_pengguna=user_id)

    tasks = []
    now = timezone.localtime()

    for profile in list_ProfileJob:
        job_items = JobItem.objects.filter(id_profile_job=profile)

        for job in job_items:
            # ✅ Cek hanya jika ada IsuAnotasi
            has_isu_anotasi = IsuAnotasi.objects.filter(id_anotasi__id_gambar=job.id_gambar).exists()

            if has_isu_anotasi:
                # Hitung deadline
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
                        tr = f"{minutes} minutes left" if minutes > 0 else "less than 1 minute"

                tasks.append({
                    'profile': profile,
                    'job': job,
                    'time_remaining': tr
                })

    context = {
        'username': username,
        'number_email': number_email,
        'tasks': tasks,
        **get_base64_images(),
        }
    return render(request, "reviewer/home_reviewer.html", context)

def task_review(request, id):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')

    username = request.session.get('username')
    number_email = request.session.get('contact')
    user_id = request.session.get('user_id')

    # ✅ Ambil profile dan pastikan milik user
    profile = get_object_or_404(ProfileJob, id_profile_job=id, id_pengguna=user_id)

    # Simpan ke session
    request.session['profile_id'] = profile.id_profile_job

    # Ambil data job terkait profile
    data_job = JobItem.objects.filter(id_profile_job=profile).select_related('id_gambar')
    total_images = data_job.count()

    context = {
        'profile_id': profile.id_profile_job,
        'total_images': total_images,
        'data_job': data_job,
        'username': username,
        'number_email': number_email,
        **get_base64_images(),
    }
    return render(request, 'reviewer/task_review.html', context)

def isu(request):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')
    username = request.session.get('username')
    number_email = request.session.get('contact')
    context={
        'username':username,
        'number_email': number_email,
        **get_base64_images(),

    }
    return render(request, 'reviewer/isu.html',context)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                pengguna = Pengguna.objects.get(nama_pengguna=username)
                if check_password(password, pengguna.password):
                    request.session['user_id'] = pengguna.id_pengguna
                    request.session['username'] = pengguna.nama_pengguna
                    member = Member.objects.filter(id_pengguna=pengguna).first()
                    if member:
                        if member.email_member:
                            request.session['contact'] = member.email_member
                        elif member.no_hp_member:
                            request.session['contact'] = member.no_hp_member
                        else:
                            request.session['contact'] = ''
                    return redirect('reviewer:home_reviewer')
                else:
                    form.add_error(None, 'Password salah')
            except Pengguna.DoesNotExist:    
                form.add_error(None, 'Username atau password salah')
            context={   
                'form':form,
                **get_base64_images(),
            }
            return render(request, 'reviewer/login.html',context)
    else:
        form = LoginForm()
        context={
            'form':form,
            **get_base64_images(),
        }
        return render(request, 'reviewer/login.html',context)

def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            peran = form.cleaned_data['peran']
            input_value = form.cleaned_data['number_email']

            # Cek email atau nomor HP
            if re.match(r"[^@]+@[^@]+\.[^@]+", input_value):
                email = input_value
                no_hp = 0
            else:
                email = ""
                no_hp = int(input_value)

            # Gabung nama lengkap
            nama_lengkap = f"{first_name} {last_name}"

            pengguna = Pengguna.objects.create(
                nama_pengguna=username,
                nama_lengkap=nama_lengkap,
                email=email,
                password=make_password(password),
                is_active=True
            )

            Member.objects.create(
                id_pengguna=pengguna,
                email_member=email,
                no_hp_member=no_hp,
                tanggal_registrasi=datetime.now(),
                afiliasi='-',
                peran=peran
            )
            
            return redirect('reviewer:login')  # ← ganti dengan URL name halaman login kamu
        else:
            # form tidak valid
            context = {
                'form': form,
                **get_base64_images()
            }
            return render(request, 'reviewer/sign_up.html', context)
    else:
        form = SignupForm()
        context = {
            'form': form,
            **get_base64_images()
        }
        return render(request, 'reviewer/sign_up.html', context)
    
def isu_anotasi(request, index):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')

    user_id = request.session.get('user_id')
    profile_id = request.session.get('profile_id')

    # ✅ Validasi bahwa profile_id benar-benar milik user yang login
    profile = ProfileJob.objects.filter(id_profile_job=profile_id, id_pengguna=user_id).first()
    if not profile:
        return redirect('reviewer:home')  # atau tampilkan pesan error

    nama_profile_job = profile.nama_profile_job.split(":")[-1].strip()

    # ✅ Ambil JobItem hanya untuk profile ini
    job_items = JobItem.objects.select_related('id_gambar').filter(
        id_profile_job=profile_id
    ).order_by('id_job_item')

    if index < 0 or index >= job_items.count():
        return redirect('reviewer:isu_anotasi', index=0)  # fallback ke index awal

    job_item = job_items[index]
    gambar = job_item.id_gambar

    segmentasi_list = Segmentasi.objects.filter(id_job_item=job_item)
    anotasi_list = Anotasi.objects.filter(id_gambar=gambar)

    # === Semantic ===
    anotasi_semantic = Anotasi.objects.select_related('id_segmentasi__id_tipe_segmentasi').filter(
        id_gambar=gambar,
        id_segmentasi__id_tipe_segmentasi=1
    )
    polygon_semantic_list = []
    for anotasi in anotasi_semantic:
        titik_list = PolygonTool.objects.filter(id_anotasi=anotasi).values_list('koordinat_xn', 'koordinat_yn')
        polygon_semantic_list.append({
            'warna': anotasi.id_segmentasi.warna_segmentasi,
            'label': anotasi.id_segmentasi.label_segmentasi,
            'points': " ".join([f"{x},{y}" for x, y in titik_list]),
        })

    # === Instance ===
    anotasi_instance = Anotasi.objects.select_related('id_segmentasi__id_tipe_segmentasi').filter(
        id_gambar=gambar,
        id_segmentasi__id_tipe_segmentasi=2
    )

    # === Panoptic ===
    anotasi_panoptic = Anotasi.objects.select_related('id_segmentasi__id_tipe_segmentasi').filter(
        id_gambar=gambar,
        id_segmentasi__id_tipe_segmentasi=3
    )
    polygon_panoptic_list = []
    for anotasi in anotasi_panoptic:
        titik_list = PolygonTool.objects.filter(id_anotasi=anotasi).values_list('koordinat_xn', 'koordinat_yn')
        polygon_panoptic_list.append({
            'warna': anotasi.id_segmentasi.warna_segmentasi,
            'label': anotasi.id_segmentasi.label_segmentasi,
            'points': " ".join([f"{x},{y}" for x, y in titik_list]),
        })

    context = {
        'username': request.session.get('username'),
        'number_email': request.session.get('contact'),
        'profile_id': profile_id,
        'nama_profile_job': nama_profile_job,
        'filename': gambar.nama_file,
        'gambar_id': gambar.id_gambar,
        'image_index': index + 1,
        'total_images': job_items.count(),
        'segmentasi_list': segmentasi_list,
        'anotasi_list': anotasi_list,
        'anotasi_box': anotasi_instance,
        'lebar_gambar': gambar.lebar,
        'tinggi_gambar': gambar.tinggi,
        'polygon_semantic_list': polygon_semantic_list,
        'polygon_panoptic_list': polygon_panoptic_list,
        'total_semantic': anotasi_semantic.count(),
        'total_instance': anotasi_instance.count(),
        'total_panoptic': anotasi_panoptic.count(),
        **get_base64_images(),
    }

    return render(request, 'reviewer/isu_anotasi.html', context)


def isu_image(request):
    if 'user_id' not in request.session:
        return redirect('reviewer:login')
    username = request.session.get('username')
    number_email = request.session.get('contact')
    context= {
        'username':username,
        'number_email':number_email,
        **get_base64_images()
    }
    return render(request, 'reviewer/isu_image.html', context)
