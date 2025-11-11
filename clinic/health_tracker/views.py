from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import HealthLog, MedicationReminder
from datetime import date, timedelta

@login_required
def health_dashboard(request):
    # Get recent health logs
    recent_logs = HealthLog.objects.filter(user=request.user)[:5]
    
    # Get active medication reminders
    active_medications = MedicationReminder.objects.filter(
        user=request.user, 
        is_active=True
    )
    
    # Get today's health log if exists
    today_log = HealthLog.objects.filter(
        user=request.user, 
        date=date.today()
    ).first()
    
    # Get health trends (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    weekly_logs = HealthLog.objects.filter(
        user=request.user,
        date__gte=week_ago
    ).order_by('date')
    
    context = {
        'recent_logs': recent_logs,
        'active_medications': active_medications,
        'today_log': today_log,
        'weekly_logs': weekly_logs,
    }
    return render(request, 'health_tracker/dashboard.html', context)

@login_required
def add_health_log(request):
    if request.method == 'POST':
        # Create new health log entry
        health_log = HealthLog.objects.create(
            user=request.user,
            date=date.today(),  # Fixed field name from log_date to date
            weight=request.POST.get('weight') or None,
            blood_pressure_systolic=request.POST.get('blood_pressure_systolic') or None,
            blood_pressure_diastolic=request.POST.get('blood_pressure_diastolic') or None,
            heart_rate=request.POST.get('heart_rate') or None,
            blood_sugar=request.POST.get('blood_sugar') or None,
            mood=request.POST.get('mood', 'good'),
            notes=request.POST.get('notes', '')
        )
        
        messages.success(request, 'Health log added successfully!')
        return redirect('health_dashboard')
    
    return render(request, 'health_tracker/add_log.html')

@login_required
def medication_reminders(request):
    medications = MedicationReminder.objects.filter(user=request.user)
    return render(request, 'health_tracker/medications.html', {'medications': medications})

@login_required
def add_medication(request):
    if request.method == 'POST':
        MedicationReminder.objects.create(
            user=request.user,
            medication_name=request.POST.get('medication_name'),
            dosage=request.POST.get('dosage'),
            frequency=request.POST.get('frequency'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Medication reminder added successfully!')
        return redirect('medication_reminders')
    
    return render(request, 'health_tracker/add_medication.html')

@login_required
def delete_health_log(request, log_id):
    health_log = get_object_or_404(HealthLog, id=log_id, user=request.user)
    health_log.delete()
    messages.success(request, 'Health log deleted successfully!')
    return redirect('health_dashboard')

@login_required
def edit_health_log(request, log_id):
    health_log = get_object_or_404(HealthLog, id=log_id, user=request.user)
    
    if request.method == 'POST':
        health_log.weight = request.POST.get('weight') or None
        health_log.blood_pressure_systolic = request.POST.get('blood_pressure_systolic') or None
        health_log.blood_pressure_diastolic = request.POST.get('blood_pressure_diastolic') or None
        health_log.heart_rate = request.POST.get('heart_rate') or None
        health_log.blood_sugar = request.POST.get('blood_sugar') or None
        health_log.mood = request.POST.get('mood', 'good')
        health_log.notes = request.POST.get('notes', '')
        health_log.save()
        
        messages.success(request, 'Health log updated successfully!')
        return redirect('health_dashboard')
    
    return render(request, 'health_tracker/edit_log.html', {'health_log': health_log})

@login_required
def delete_medication(request, med_id):
    medication = get_object_or_404(MedicationReminder, id=med_id, user=request.user)
    medication.delete()
    messages.success(request, 'Medication reminder deleted successfully!')
    return redirect('medication_reminders')
