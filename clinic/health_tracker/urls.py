from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_dashboard, name='health_dashboard'),
    path('add-log/', views.add_health_log, name='add_health_log'),
    path('edit-log/<int:log_id>/', views.edit_health_log, name='edit_health_log'),
    path('delete-log/<int:log_id>/', views.delete_health_log, name='delete_health_log'),
    path('medications/', views.medication_reminders, name='medication_reminders'),
    path('add-medication/', views.add_medication, name='add_medication'),
    path('delete-medication/<int:med_id>/', views.delete_medication, name='delete_medication'),
]
