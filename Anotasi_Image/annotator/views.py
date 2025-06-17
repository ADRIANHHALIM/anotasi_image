from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def annotate_view(request):
    """
    View for the main annotation page
    """
    context = {
        'current_page': 'annotate',
        'user': request.user,
    }
    return render(request, 'annotator/annotate.html', context)

@login_required
def notifications_view(request):
    """
    View for the notifications page
    """
    context = {
        'current_page': 'notifications',
        'user': request.user,
        'notifications': [],  # TODO: Implement notification system
    }
    return render(request, 'annotator/notifications.html', context)
