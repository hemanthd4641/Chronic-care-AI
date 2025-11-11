from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Appointment
from .forms import AppointmentForm

# Patient: Book Appointment
@login_required
def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect("appointments:my_appointments")
    else:
        form = AppointmentForm(user=request.user)
    return render(request, "appointments/book_appointment.html", {"form": form})

# Patient: View My Appointments
@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by("-date", "-time")
    return render(request, "appointments/my_appointments.html", {"appointments": appointments})

# Doctor: View Appointments
@login_required
def doctor_appointments(request):
    # show only the appointments where the logged-in user is the doctor
    appointments = Appointment.objects.filter(doctor=request.user)
    stats = {
        "total": appointments.count(),
        "pending": appointments.filter(status="Pending").count(),
        "confirmed": appointments.filter(status="Confirmed").count(),
        "cancelled": appointments.filter(status="Cancelled").count(),
    }
    return render(request, "appointments/doctor_appointments.html", {"appointments": appointments, "stats": stats})
@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.delete()
    return redirect("appointments:my_appointments")


@login_required
@require_POST
def update_appointment_status(request):
    """Allow doctors to update the status of their appointments via AJAX."""
    appt_id = request.POST.get("id")
    new_status = request.POST.get("status")
    valid_statuses = {"Pending", "Confirmed", "Cancelled"}
    if new_status not in valid_statuses:
        return JsonResponse({"ok": False, "error": "Invalid status"}, status=400)

    appt = get_object_or_404(Appointment, id=appt_id, doctor=request.user)
    appt.status = new_status
    appt.save(update_fields=["status"])
    return JsonResponse({"ok": True, "status": appt.status})