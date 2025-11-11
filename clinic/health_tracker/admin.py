from django.contrib import admin
from .models import HealthLog, MedicationReminder

@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'mood']
    list_filter = ['date', 'mood', 'user']
    search_fields = ['user__username', 'notes']

@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'medication_name', 'dosage', 'frequency', 'start_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'user']
    search_fields = ['user__username', 'medication_name']
