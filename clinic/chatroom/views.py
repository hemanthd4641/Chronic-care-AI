from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chats, Report
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def view_chatroom(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        message = request.POST.get('message')
        user = request.user
        # Save the chat message
        chat = Chats(user=user, message=message)
        chat.save()
        # Respond with the new chat data
        return JsonResponse({
            'user': user.username,
            'message': chat.message,
            'created': chat.created.strftime('%Y-%m-%d %H:%M:%S')
        })
    # For GET requests, render the template
    chats = Chats.objects.all()
    context = {'chats': chats}
    return render(request, 'chatroom/index.html', context)

@login_required
def add_new_report(request):
    if request.method == 'POST' and not request.user.is_superuser:
        # Only non-superusers (patients) can submit reports
        report_title = request.POST.get('report_title')
        report_text = request.POST.get('report')
        category = request.POST.get('category')
        priority = request.POST.get('priority')
        rating = request.POST.get('rating')
        
        if report_text:
            # Set default priority if none provided
            priority_value = priority if priority else 'low'
            
            Report.objects.create(
                user=request.user,
                report_title=report_title,
                report=report_text,
                category=category,
                priority=priority_value,
                rating=rating
            )
            messages.success(request, 'Your report has been submitted successfully!')
            return redirect('chatroom:report')
        else:
            messages.error(request, 'Please provide a report description.')

    # Get reports based on user type
    if request.user.is_superuser:
        # Superusers see all reports ordered by newest first and priority
        reports = Report.objects.all().order_by('-created', '-priority')
    else:
        # Regular users see only their own reports ordered by newest first
        reports = Report.objects.filter(user=request.user).order_by('-created')
    
    context = {'reports': reports}
    return render(request, 'chatroom/report.html', context)

@login_required
def recived_report(request, pk):
    # Only superusers can mark reports as received
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('chatroom:report')
    
    report = Report.objects.get(pk=pk)
    report.recived = True
    report.save()
    
    messages.success(request, f'Report "{report.report_title or f"#{report.id}"}" from {report.user.username} has been marked as received.')
    return redirect('chatroom:report')