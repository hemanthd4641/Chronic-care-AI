from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import PrivateMessage, ChatRoomMessage
from .forms import PrivateMessageForm, ChatRoomMessageForm
import json

@login_required
def private_messages(request):
    """View private messages for the current user"""
    if request.user.is_superuser:
        # Doctor sees messages from all patients
        received_messages = PrivateMessage.objects.filter(recipient=request.user)
        sent_messages = PrivateMessage.objects.filter(sender=request.user)
    else:
        # Patient sees messages with doctors
        received_messages = PrivateMessage.objects.filter(recipient=request.user)
        sent_messages = PrivateMessage.objects.filter(sender=request.user)
    
    # Mark received messages as read
    received_messages.filter(is_read=False).update(is_read=True)
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': PrivateMessage.objects.filter(recipient=request.user, is_read=False).count()
    }
    return render(request, 'messaging/private_messages.html', context)

@login_required
def send_private_message(request):
    """Send a private message"""
    if request.method == 'POST':
        form = PrivateMessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('messaging:private_messages')
    else:
        form = PrivateMessageForm(user=request.user)
    
    return render(request, 'messaging/send_message.html', {'form': form})

@login_required
def view_message(request, message_id):
    """View a specific message"""
    message = get_object_or_404(PrivateMessage, id=message_id)
    
    # Ensure user can only view their own messages
    if message.sender != request.user and message.recipient != request.user:
        return redirect('messaging:private_messages')
    
    # Mark as read if recipient is viewing
    if message.recipient == request.user:
        message.mark_as_read()
    
    return render(request, 'messaging/view_message.html', {'message': message})

@login_required
def doctor_patient_messages(request):
    """Doctor view to see all patient messages"""
    if not request.user.is_superuser:
        return redirect('messaging:private_messages')
    
    # Get all messages where doctor is recipient
    messages = PrivateMessage.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Group messages by sender
    patients = User.objects.filter(is_superuser=False).distinct()
    patient_messages = {}
    
    for patient in patients:
        patient_messages[patient] = PrivateMessage.objects.filter(
            sender=patient, 
            recipient=request.user
        ).order_by('-created_at')[:5]  # Last 5 messages per patient
    
    context = {
        'patient_messages': patient_messages,
        'total_messages': messages.count(),
        'unread_count': messages.filter(is_read=False).count()
    }
    return render(request, 'messaging/doctor_patient_messages.html', context)

@login_required
def chat_room(request):
    """Enhanced chat room for all users"""
    if request.method == 'POST':
        form = ChatRoomMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect('messaging:chat_room')
    else:
        form = ChatRoomMessageForm()
    
    # Get last 50 messages
    messages = ChatRoomMessage.objects.all()[:50]
    
    context = {
        'form': form,
        'messages': messages,
        'user_count': User.objects.filter(is_active=True).count()
    }
    return render(request, 'messaging/chat_room.html', context)

@login_required
@require_POST
@csrf_exempt
def send_chat_message(request):
    """AJAX endpoint to send chat messages"""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if message_text:
            ChatRoomMessage.objects.create(
                user=request.user,
                message=message_text
            )
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def get_chat_messages(request):
    """AJAX endpoint to get latest chat messages"""
    try:
        messages = ChatRoomMessage.objects.all()[:20]
        message_data = []
        
        for msg in messages:
            message_data.append({
                'id': msg.id,
                'user': msg.user.username,
                'message': msg.message,
                'timestamp': msg.created_at.strftime('%H:%M'),
                'is_doctor': msg.user.is_superuser
            })
        
        return JsonResponse({'messages': message_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})