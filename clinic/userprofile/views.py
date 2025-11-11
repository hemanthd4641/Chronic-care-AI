from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.db.models import Q
from django.contrib import messages

# Create your views here.
@login_required
def index(request):
    # Show only the current user's profile
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        # Create a profile if it doesn't exist
        profile = Profile.objects.create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        
        # Update profile fields
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.birth_date = request.POST.get('birth_date') or None
        profile.phone = request.POST.get('phone', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('userprofile:profile')
    
    return redirect('userprofile:profile')