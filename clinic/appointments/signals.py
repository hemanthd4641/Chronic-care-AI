from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Appointment


@receiver(post_save, sender=Appointment)
def email_doctor_on_create(sender, instance: Appointment, created: bool, **kwargs):
    if not created:
        return
    doctor = instance.doctor
    if not getattr(doctor, "email", None):
        return
    context = {"appt": instance}
    html = render_to_string("emails/appointment_created.html", context)
    subject = f"New appointment from {instance.patient.get_full_name() or instance.patient.username}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[doctor.email],
    )
    msg.attach_alternative(html, "text/html")
    try:
        msg.send(fail_silently=True)
    except Exception:
        pass


@receiver(pre_save, sender=Appointment)
def email_patient_on_status_change(sender, instance: Appointment, **kwargs):
    if not instance.pk:
        return
    try:
        old = Appointment.objects.get(pk=instance.pk)
    except Appointment.DoesNotExist:
        return
    if old.status == instance.status:
        return
    patient = instance.patient
    if not getattr(patient, "email", None):
        return
    context = {"old": old, "new": instance}
    html = render_to_string("emails/appointment_status_changed.html", context)
    subject = f"Your appointment status: {instance.status}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[patient.email],
    )
    msg.attach_alternative(html, "text/html")
    try:
        msg.send(fail_silently=True)
    except Exception:
        pass



