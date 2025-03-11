from django.shortcuts import render, redirect
from .forms import UserForm

def create_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')
    else:
        form = UserForm()

    return render(request, "user_form.html", {"form": form})
