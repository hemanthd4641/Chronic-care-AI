from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegForm,LoginForm,updateForm
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .models import Student, Announcements, DoctorPatientRelationship
from django import forms
from userprofile.models import Profile
from django.contrib import messages
from django.utils import timezone
from appointments.models import Appointment
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import IntegrityError
@login_required
def registration(request):
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            try:
                user = User(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )
                user.set_password(form.cleaned_data['password1'])  
                user.save() 
                profile = Profile(user = user)
                profile.save()
                student = form.save(commit=False)
                student.user = user
                # Set the creator of the patient account (the current logged-in user)
                if request.user.is_superuser:
                    student.created_by = request.user
                student.save()
                print(f"Debug: Created student {student.first_name} {student.last_name} with ID {student.id}")

                # Automatically create a doctor-patient relationship if the registrar is a doctor
                if request.user.is_superuser:
                    DoctorPatientRelationship.objects.get_or_create(
                        doctor=request.user,
                        patient=user,
                        defaults={'is_active': True}
                    )

                messages.success(request, 'Registration successful!')
                return redirect('admission:index')
            except IntegrityError as e:
                # Handle database integrity errors gracefully
                if 'username' in str(e):
                    form.add_error('username', 'A user with this username already exists. Please choose a different username.')
                elif 'email' in str(e):
                    form.add_error('email', 'A user with this email address already exists. Please use a different email.')
                else:
                    form.add_error(None, 'Registration failed due to a database error. Please try again.')
    else:
        form = RegForm()

    context = {'form': form}
    return render(request, 'admission/register.html', context)
def LoginView(request):
    page = 'login'
    error = False
    if(request.user.is_authenticated):
        return redirect('admission:index')
    form = LoginForm() 
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')  
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print('user logged in successfull')
                return redirect('admission:index')  
            else:
                  error = "invalid user or password"
    context = {'page': page, 'form': form,'error':error}  
    return render(request, 'admission/login.html', context)  

@login_required
def index(request):
    print("Index view accessed in admission")
    studentcount = Student.objects.count()
    announcements = Announcements.objects.all()[0:3]
    
    # Get the doctor who created the patient account
    created_by_doctor = None
    assigned_doctor = None
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            # Get the student record to find the creator
            student = Student.objects.get(user=request.user)
            if student.created_by:
                created_by_doctor = student.created_by
        except Student.DoesNotExist:
            pass
        
        # Also get currently assigned doctor (if different from creator)
        try:
            relationship = DoctorPatientRelationship.objects.get(patient=request.user, is_active=True)
            assigned_doctor = relationship.doctor
        except DoctorPatientRelationship.DoesNotExist:
            assigned_doctor = None
    
    context = {
        'studentcount': studentcount,
        'announcements': announcements,
        'created_by_doctor': created_by_doctor,
        'assigned_doctor': assigned_doctor
    }

    # If current user is a doctor (superuser in this app), include their appointment stats
    if request.user.is_authenticated and request.user.is_superuser:
        today = timezone.now().date()
        doctor_today_appointments = Appointment.objects.filter(doctor=request.user, date=today).count()
        doctor_total_pending = Appointment.objects.filter(doctor=request.user, status="Pending").count()
        doctor_total_confirmed = Appointment.objects.filter(doctor=request.user, status="Confirmed").count()
        context.update({
            'doctor_today_appointments': doctor_today_appointments,
            'doctor_total_pending': doctor_total_pending,
            'doctor_total_confirmed': doctor_total_confirmed,
        })

    return render(request,'admission/index.html',context)


@login_required
def project_summary(request):
    """Generate an HTML summary page which the user can print to PDF from the browser."""
    context = {
        'user': request.user,
        'apps': [
            'admission', 'appointments', 'chatbot', 'chatroom', 'health_tracker',
            'hostel', 'medical_store', 'messaging', 'predictor', 'timetable', 'userprofile'
        ],
        'features': [
            'Authentication and role-based flows',
            'Patient registration and management',
            'Doctor-patient assignments',
            'Appointments booking and doctor status updates',
            'Private messaging and doctor-patient message overview',
            'Community chat and feedback reports',
            'Prediction room with ML models and history/compare charts',
            'Health tracker with logs and medications',
            'Medical store cart and payments link',
        ],
    }
    html = render_to_string('summary.html', context)
    return HttpResponse(html)

def LogoutView(request):
    logout(request)
    return redirect('admission:login')
@login_required
def veiewStudents(request):
    students = Student.objects.all()
    print(f"Debug: Found {students.count()} students")
    
    # Check for users without student records
    all_users = User.objects.filter(is_superuser=False)
    users_with_students = User.objects.filter(student__isnull=False)
    users_without_students = all_users.exclude(id__in=users_with_students.values_list('id', flat=True))
    
    print(f"Debug: Total non-superusers: {all_users.count()}")
    print(f"Debug: Users with student records: {users_with_students.count()}")
    print(f"Debug: Users without student records: {users_without_students.count()}")
    
    if users_without_students.exists():
        print("Users without student records:")
        for user in users_without_students:
            print(f"  - {user.username} ({user.first_name} {user.last_name})")
    
    for student in students:
        print(f"Student: {student.first_name} {student.last_name} - {student.email}")
    
    context = {'students': students}
    return render(request, 'admission/students.html', context)
@login_required
def deletestudent(request, pk):
    student = User.objects.get(pk = pk)
    student.delete()
    return redirect('admission:viewstudents')
@login_required
def updatedetails(request, pk):
    try:
        user = User.objects.get(pk=pk)
        student = Student.objects.get(user=user)
    except (User.DoesNotExist, Student.DoesNotExist):
        messages.error(request, 'Student not found.')
        return redirect('admission:viewstudents')
    
    form = updateForm(instance=student)

    if request.method == 'POST':
        form = updateForm(request.POST, instance=student)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Successfully updated details for {user.username}.')
                return redirect('admission:viewstudents')
            except Exception as e:
                messages.error(request, f'Error updating details: {str(e)}')
        else:
            # Add form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')

    context = {'form': form, 'student': student, 'user': user}
    return render(request, 'admission/updatedetails.html', context)



@login_required
def announcement_view(request):
    announcements = Announcements.objects.all()
    if(request.method == 'POST'):
        about = request.POST.get('about')
        body = request.POST.get('body')
        announcement = Announcements(
            about = about,body = body
        )
        announcement.save()
        # Email announcement to all active patients (non-superusers)
        recipients = list(User.objects.filter(is_active=True, is_superuser=False).exclude(email="").values_list("email", flat=True))
        if recipients:
            html = render_to_string('emails/announcement.html', {"a": announcement})
            subject = f"Announcement: {announcement.about}"
            chunk = 50
            for i in range(0, len(recipients), chunk):
                bcc = recipients[i:i+chunk]
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body="",
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    bcc=bcc,
                )
                msg.attach_alternative(html, 'text/html')
                try:
                    msg.send(fail_silently=True)
                except Exception:
                    pass
        return redirect("admission:announcement")
    context = {"announcements":announcements}
    return render(request,'admission/announcement.html',context)

@login_required
def deleteAnnouncements(request, pk):
    try:
        announcement = Announcements.objects.get(pk=pk)
        announcement.delete()
    except Announcements.DoesNotExist:
        pass  

    return redirect("admission:announcement")

@login_required
def manage_patient_assignments(request):
    """View for doctors to manage patient assignments"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('admission:index')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        action = request.POST.get('action')
        
        if action == 'assign':
            try:
                patient = User.objects.get(id=patient_id, is_superuser=False)
                doctor = User.objects.get(id=doctor_id, is_superuser=True)
                
                # Deactivate any existing relationship
                DoctorPatientRelationship.objects.filter(
                    patient=patient, is_active=True
                ).update(is_active=False)
                
                # Create new relationship
                relationship, created = DoctorPatientRelationship.objects.get_or_create(
                    doctor=doctor,
                    patient=patient,
                    defaults={'is_active': True}
                )
                
                if created:
                    messages.success(request, f'Successfully assigned {patient.username} to {doctor.username}')
                else:
                    relationship.is_active = True
                    relationship.save()
                    messages.success(request, f'Updated assignment: {patient.username} to {doctor.username}')
                    
            except User.DoesNotExist:
                messages.error(request, 'Invalid patient or doctor selected.')
        
        elif action == 'unassign':
            try:
                patient = User.objects.get(id=patient_id, is_superuser=False)
                DoctorPatientRelationship.objects.filter(
                    patient=patient, is_active=True
                ).update(is_active=False)
                messages.success(request, f'Unassigned {patient.username} from all doctors.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid patient selected.')
    
    # Get all patients and their current assignments
    patients = User.objects.filter(is_superuser=False).order_by('username')
    doctors = User.objects.filter(is_superuser=True).order_by('username')
    
    # Get current assignments
    assignments = {}
    for patient in patients:
        try:
            relationship = DoctorPatientRelationship.objects.get(patient=patient, is_active=True)
            assignments[patient.id] = relationship.doctor
        except DoctorPatientRelationship.DoesNotExist:
            assignments[patient.id] = None
    
    context = {
        'patients': patients,
        'doctors': doctors,
        'assignments': assignments,
    }
    
    return render(request, 'admission/manage_assignments.html', context) 

@login_required
def sync_missing_students(request):
    """Create Student records for Users who don't have them"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('admission:index')
    
    # Find users without student records (excluding superusers)
    users_without_students = User.objects.filter(
        is_superuser=False,
        student__isnull=True
    )
    
    created_count = 0
    
    for user in users_without_students:
        try:
            student = Student.objects.create(
                user=user,
                first_name=user.first_name or 'Unknown',
                last_name=user.last_name or 'Unknown',
                username=user.username,
                password1='',  # Empty since we don't store plain passwords
                password2='',  # Empty since we don't store plain passwords
                dob='2000-01-01',  # Default date - should be updated later
                gender='Other',  # Default gender - should be updated later
                email=user.email or f'{user.username}@example.com',
                phone_number=0,  # Default phone - should be updated later
                address='Not provided'  # Default address - should be updated later
            )
            created_count += 1
            messages.success(request, f'Created Student record for user: {user.username}')
        except Exception as e:
            messages.error(request, f'Failed to create Student record for user {user.username}: {str(e)}')
    
    if created_count > 0:
        messages.success(request, f'Successfully created {created_count} Student records')
    else:
        messages.info(request, 'No users found that need Student records')
    
    return redirect('admission:viewstudents') 
    