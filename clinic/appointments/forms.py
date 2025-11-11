from django import forms
from django.contrib.auth.models import User
from .models import Appointment
from admission.models import DoctorPatientRelationship

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time", "reason"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            # For patients, only show their assigned doctor
            try:
                relationship = DoctorPatientRelationship.objects.get(patient=user, is_active=True)
                self.fields['doctor'].queryset = User.objects.filter(id=relationship.doctor.id)
                self.fields['doctor'].initial = relationship.doctor
                self.fields['doctor'].widget.attrs['readonly'] = True
                self.fields['doctor'].widget.attrs['class'] = 'form-control bg-light'
            except DoctorPatientRelationship.DoesNotExist:
                # If no doctor is assigned, allow booking with any available doctor (admins)
                fallback_qs = User.objects.filter(is_superuser=True)
                self.fields['doctor'].queryset = fallback_qs
                if fallback_qs.exists():
                    self.fields['doctor'].help_text = "No assigned doctor found. Select an available doctor."
                else:
                    self.fields['doctor'].help_text = "No doctors available. Please contact admin."
        else:
            # For doctors/admins, show all doctors
            self.fields['doctor'].queryset = User.objects.filter(is_superuser=True)
