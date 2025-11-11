from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("book/", views.book_appointment, name="book_appointment"),
    path("my/", views.my_appointments, name="my_appointments"),
    path("doctor/", views.doctor_appointments, name="doctor_appointments"),
    path("delete/<int:appointment_id>/", views.delete_appointment, name="delete_appointment"),
    path("update-status/", views.update_appointment_status, name="update_status"),
]