import os
import json
from typing import List, Optional, Dict, Any
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from admission.models import Student, DoctorPatientRelationship
from messaging.models import PrivateMessage, ChatRoomMessage
from appointments.models import Appointment
from predictor.models import PredictionHistory

# Add this import for the Announcements model
try:
    from admission.models import Announcements
except ImportError:
    # Fallback if the model is in a different location
    from django.contrib.auth.models import Group
    Announcements = None

class AIAgent:
    """Enhanced AI Agent that can perform various services based on user roles"""
    
    def __init__(self, user: User):
        self.user = user
        self.is_doctor = user.is_superuser
        self.is_patient = not user.is_superuser and not user.is_staff
    
    def _check_doctor_access(self) -> bool:
        """Check if the current user has doctor-level access"""
        return self.is_doctor
    
    def _check_patient_access(self) -> bool:
        """Check if the current user has patient-level access"""
        return self.is_patient or self.is_doctor  # Doctors can also access patient features
    
    def register_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient (doctor only)"""
        if not self._check_doctor_access():
            return {"success": False, "message": "Only doctors can register patients"}
        
        try:
            # Create user account
            user = User(
                username=patient_data['username'],
                email=patient_data['email'],
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
            )
            user.set_password(patient_data['password'])
            user.save()
            
            # Create student profile
            student = Student.objects.create(
                user=user,
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
                username=patient_data['username'],
                email=patient_data['email'],
                dob=patient_data['dob'],
                gender=patient_data['gender'],
                phone_number=patient_data['phone_number'],
                address=patient_data['address'],
                password1=patient_data['password'],
                password2=patient_data['password']
            )
            
            return {
                "success": True, 
                "message": f"✅ Patient {patient_data['first_name']} {patient_data['last_name']} registered successfully with username: {patient_data['username']}"
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Registration failed: {str(e)}"}
    
    def view_patients(self, filter_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """View patient information (doctor only)"""
        if not self._check_doctor_access():
            return {"success": False, "message": "Only doctors can view patient information"}
        
        try:
            # Get all patients assigned to this doctor
            relationships = DoctorPatientRelationship.objects.filter(
                doctor=self.user, 
                is_active=True
            ).select_related('patient', 'patient__student')
            
            patients = []
            for rel in relationships:
                patient = rel.patient
                try:
                    student_info = patient.student
                    patient_data = {
                        "id": patient.id,
                        "username": patient.username,
                        "first_name": patient.first_name,
                        "last_name": patient.last_name,
                        "email": patient.email,
                        "dob": student_info.dob,
                        "gender": student_info.gender,
                        "phone_number": student_info.phone_number,
                        "address": student_info.address,
                    }
                except Student.DoesNotExist:
                    # Fallback if student record doesn't exist
                    patient_data = {
                        "id": patient.id,
                        "username": patient.username,
                        "first_name": patient.first_name,
                        "last_name": patient.last_name,
                        "email": patient.email,
                        "dob": "Not provided",
                        "gender": "Not provided",
                        "phone_number": "Not provided",
                        "address": "Not provided",
                    }
                patients.append(patient_data)
            
            if patients:
                patient_list = "\n".join([
                    f"👤 {p['first_name']} {p['last_name']} (Username: {p['username']}, ID: {p['id']})"
                    for p in patients
                ])
                return {
                    "success": True,
                    "message": f"📋 **Your Patients** ({len(patients)} total):\n\n{patient_list}"
                }
            else:
                return {
                    "success": True,
                    "message": "📋 You don't have any patients assigned yet."
                }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve patients: {str(e)}"}
    
    def view_feedback(self) -> Dict[str, Any]:
        """View feedback/messages for the user"""
        try:
            if self._check_doctor_access():
                # Doctors see messages from patients
                messages = PrivateMessage.objects.filter(recipient=self.user).order_by('-created_at')[:20]
            else:
                # Patients see their own messages
                messages = PrivateMessage.objects.filter(
                    recipient=self.user
                ).order_by('-created_at')[:20]
            
            feedback_data = []
            for msg in messages:
                # Get the sender's name
                sender_name = msg.sender.username
                if not self._check_doctor_access():
                    # For patients, show doctor's name if available
                    try:
                        relationship = DoctorPatientRelationship.objects.get(patient=self.user, is_active=True)
                        sender_name = f"Dr. {relationship.doctor.username}"
                    except DoctorPatientRelationship.DoesNotExist:
                        pass
                
                feedback_data.append({
                    "id": msg.id,
                    "from": sender_name,
                    "subject": msg.subject,
                    "message": msg.message,
                    "timestamp": msg.created_at.strftime('%Y-%m-%d %H:%M'),
                    "is_read": "✅" if msg.is_read else "❌"
                })
            
            if feedback_data:
                message_list = "\n".join([
                    f"📩 {f['subject']} - From: {f['from']} - {f['timestamp']} {f['is_read']}"
                    for f in feedback_data
                ])
                return {
                    "success": True,
                    "message": f"📬 **Your Messages** ({len(feedback_data)} recent):\n\n{message_list}"
                }
            else:
                return {
                    "success": True,
                    "message": "📬 You don't have any messages yet."
                }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve messages: {str(e)}"}
    
    def view_appointments(self) -> Dict[str, Any]:
        """View appointments based on user role"""
        try:
            if self._check_doctor_access():
                # Doctors see their appointments
                appointments = Appointment.objects.filter(doctor=self.user).order_by('-date', '-time')[:20]
            else:
                # Patients see their appointments
                appointments = Appointment.objects.filter(patient=self.user).order_by('-date', '-time')[:20]
            
            appointment_data = []
            for appt in appointments:
                appointment_data.append({
                    "id": appt.id,
                    "date": appt.date.strftime('%Y-%m-%d'),
                    "time": appt.time.strftime('%H:%M'),
                    "reason": appt.reason,
                    "status": appt.status,
                    "doctor": appt.doctor.username if not self._check_doctor_access() else None,
                    "patient": appt.patient.username if self._check_doctor_access() else None
                })
            
            if appointment_data:
                if self._check_doctor_access():
                    appt_list = "\n".join([
                        f"📅 {a['date']} at {a['time']} - Patient: {a['patient']} - Reason: {a['reason']} - Status: {a['status']}"
                        for a in appointment_data
                    ])
                else:
                    appt_list = "\n".join([
                        f"📅 {a['date']} at {a['time']} - Doctor: Dr. {a['doctor']} - Reason: {a['reason']} - Status: {a['status']}"
                        for a in appointment_data
                    ])
                return {
                    "success": True,
                    "message": f"🗓️ **Your Appointments** ({len(appointment_data)} upcoming):\n\n{appt_list}"
                }
            else:
                return {
                    "success": True,
                    "message": "🗓️ You don't have any appointments scheduled."
                }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve appointments: {str(e)}"}
    
    def view_prediction_history(self) -> Dict[str, Any]:
        """View prediction history for patients or all patients for doctors"""
        try:
            if self._check_doctor_access():
                # Doctors can see all prediction history
                histories = PredictionHistory.objects.select_related('user').order_by('-created_at')[:50]
            else:
                # Patients see their own history
                histories = PredictionHistory.objects.filter(user=self.user).order_by('-created_at')[:20]
            
            history_data = []
            for history in histories:
                history_data.append({
                    "id": history.id,
                    "disease_type": history.get_disease_display(),
                    "result": history.get_result_display(),
                    "confidence": f"{history.confidence*100:.1f}%" if history.confidence else "N/A",
                    "date": history.created_at.strftime('%Y-%m-%d %H:%M'),
                    "patient": history.user.username if self._check_doctor_access() else None
                })
            
            if history_data:
                if self._check_doctor_access():
                    history_list = "\n".join([
                        f"📊 {h['disease_type']}: {h['result']} ({h['confidence']}) on {h['date']} - Patient: {h['patient']}"
                        for h in history_data
                    ])
                else:
                    history_list = "\n".join([
                        f"📊 {h['disease_type']}: {h['result']} ({h['confidence']}) on {h['date']}"
                        for h in history_data
                    ])
                return {
                    "success": True,
                    "message": f"📈 **Prediction History** ({len(history_data)} records):\n\n{history_list}"
                }
            else:
                return {
                    "success": True,
                    "message": "📈 You don't have any prediction history yet."
                }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve prediction history: {str(e)}"}
    
    def assign_doctor_to_patient(self, patient_id: int, doctor_id: int) -> Dict[str, Any]:
        """Assign a doctor to a patient (admin/doctor only)"""
        if not self._check_doctor_access():
            return {"success": False, "message": "Only doctors can assign patients"}
        
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
                message = f"✅ Successfully assigned {patient.username} to Dr. {doctor.username}"
            else:
                relationship.is_active = True
                relationship.save()
                message = f"✅ Updated assignment: {patient.username} is now assigned to Dr. {doctor.username}"
                
            return {"success": True, "message": message}
        except User.DoesNotExist:
            return {"success": False, "message": "❌ Invalid patient or doctor selected"}
        except Exception as e:
            return {"success": False, "message": f"❌ Assignment failed: {str(e)}"}
    
    def create_announcement(self, title: str, content: str) -> Dict[str, Any]:
        """Create an announcement (doctor only)"""
        if not self._check_doctor_access():
            return {"success": False, "message": "Only doctors can create announcements"}
        
        # Check if Announcements model is available
        if Announcements is None:
            return {"success": False, "message": "Announcements feature is not available"}
        
        try:
            # Create the announcement
            announcement = Announcements.objects.create(
                about=title,
                body=content
            )
            
            # Email announcement to all active patients (non-superusers)
            recipients = list(User.objects.filter(is_active=True, is_superuser=False).exclude(email="").values_list("email", flat=True))
            if recipients:
                html = render_to_string('emails/announcement.html', {"a": announcement})
                subject = f"📢 Announcement: {announcement.about}"
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
            
            return {
                "success": True, 
                "message": f"✅ Announcement '{title}' created successfully and emailed to {len(recipients)} patients"
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to create announcement: {str(e)}"}
    
    def view_announcements(self) -> Dict[str, Any]:
        """View recent announcements"""
        # Check if Announcements model is available
        if Announcements is None:
            return {"success": False, "message": "Announcements feature is not available"}
        
        try:
            announcements = Announcements.objects.all().order_by('-created_at')[:10]
            
            if announcements:
                ann_list = "\n".join([
                    f"📢 {a.about} - {a.created.strftime('%Y-%m-%d')}\n   {a.body[:100]}{'...' if len(a.body) > 100 else ''}"
                    for a in announcements
                ])
                return {
                    "success": True,
                    "message": f"🗞️ **Recent Announcements** ({len(announcements)}):\n\n{ann_list}"
                }
            else:
                return {
                    "success": True,
                    "message": "🗞️ No recent announcements."
                }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve announcements: {str(e)}"}
    
    def view_profile(self) -> Dict[str, Any]:
        """View user profile information"""
        try:
            profile_data = {
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "is_doctor": self.is_doctor,
                "date_joined": self.user.date_joined.strftime('%Y-%m-%d %H:%M')
            }
            
            # Add patient-specific information if applicable
            if not self._check_doctor_access():
                try:
                    student = Student.objects.get(user=self.user)
                    profile_data.update({
                        "dob": student.dob.strftime('%Y-%m-%d') if student.dob else "Not provided",
                        "gender": student.gender if student.gender else "Not provided",
                        "phone_number": student.phone_number if student.phone_number else "Not provided",
                        "address": student.address if student.address else "Not provided"
                    })
                except Student.DoesNotExist:
                    pass
            
            # Add doctor-specific information if applicable
            if self._check_doctor_access():
                # Count assigned patients
                patient_count = DoctorPatientRelationship.objects.filter(
                    doctor=self.user, 
                    is_active=True
                ).count()
                
                profile_data.update({
                    "assigned_patients": patient_count
                })
            
            # Format the profile information nicely
            profile_info = f"""👤 **Your Profile Information**
====================
- Username: {profile_data['username']}
- Name: {profile_data['first_name']} {profile_data['last_name']}
- Email: {profile_data['email']}
- Role: {'Doctor' if profile_data['is_doctor'] else 'Patient'}
- Member since: {profile_data['date_joined']}"""
                
            if not profile_data['is_doctor']:
                profile_info += f"""
                
🏥 **Patient Information**
- Date of Birth: {profile_data.get('dob', 'Not provided')}
- Gender: {profile_data.get('gender', 'Not provided')}
- Phone: {profile_data.get('phone_number', 'Not provided')}
- Address: {profile_data.get('address', 'Not provided')}"""
            else:
                profile_info += f"""
                
👥 **Doctor Information**
- Assigned Patients: {profile_data.get('assigned_patients', 0)}"""
            
            return {
                "success": True,
                "message": profile_info
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Failed to retrieve profile: {str(e)}"}
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process natural language commands and route to appropriate functions"""
        command = command.lower().strip()
        
        # Debug: Print the command being processed
        print(f"Processing command: {command}")
        
        # Registration command
        if ("register" in command and "patient" in command) or "new patient" in command:
            if not self._check_doctor_access():
                return {"success": False, "message": "Only doctors can register patients"}
            return {"success": True, "message": "To register a new patient, please use the registration form in the web interface or ask your system administrator for assistance."}
        
        # View patients command
        elif ("view" in command or "see" in command or "list" in command or "show" in command) and "patient" in command:
            return self.view_patients()
        
        # View feedback/messages command
        elif ("view" in command or "see" in command or "show" in command) and ("feedback" in command or "message" in command or "inbox" in command):
            return self.view_feedback()
        
        # View appointments command
        elif ("view" in command or "see" in command or "show" in command) and "appointment" in command:
            return self.view_appointments()
        
        # View prediction history command
        elif ("view" in command or "see" in command or "show" in command) and ("prediction" in command or "history" in command):
            return self.view_prediction_history()
        
        # Create announcement command
        elif ("create" in command or "make" in command) and "announcement" in command:
            if self._check_doctor_access():
                return {"success": True, "message": "To create an announcement, please use the announcement form in the web interface."}
            else:
                return {"success": False, "message": "Only doctors can create announcements"}
        
        # View announcements command
        elif ("view" in command or "see" in command or "show" in command) and "announcement" in command:
            return self.view_announcements()
        
        # Assign doctor command
        elif "assign" in command and "doctor" in command and "patient" in command:
            if self._check_doctor_access():
                return {"success": True, "message": "To assign a doctor to a patient, please use the patient management interface."}
            else:
                return {"success": False, "message": "Only doctors can assign patients to doctors"}
        
        # View profile command
        elif ("view" in command or "see" in command or "show" in command) and "profile" in command:
            return self.view_profile()
        
        # Medical queries - detect and handle medical questions
        elif any(word in command for word in ["medical", "health", "disease", "symptom", "treatment", "medicine", "doctor", "pain", "condition", "diabetes", "heart", "hypertension", "kidney"]):
            # For medical queries, we'll return a special response that indicates
            # the main chatbot should handle this with the AI medical functionality
            return {"action": "medical_query", "query": command}
        
        # Help command
        elif "help" in command:
            help_message = (
                "🤖 **AI Assistant Help**\n"
                "==================\n\n"
                "I can help you with the following:\n\n"
                "📋 **Patient Management** (Doctors only):\n"
                "  • View patient information\n\n"
                "📬 **Communication**:\n"
                "  • View your messages/feedback\n"
                "  • View announcements\n\n"
                "📅 **Appointments**:\n"
                "  • View your appointments\n\n"
                "📊 **Health Records**:\n"
                "  • View prediction history\n"
                "  • View your profile\n\n"
                "⚕️ **Medical Information**:\n"
                "  • Ask about symptoms, diseases, treatments\n\n"
                "**Try commands like:**\n"
                "• 'View my appointments'\n"
                "• 'Show my profile'\n"
                "• 'What are symptoms of diabetes?'\n"
                "• 'View patient list' (doctors only)"
            )
            return {"success": True, "message": help_message}
        
        # Default response for unrecognized commands
        else:
            return {
                "success": False,
                "message": (
                    "❓ I didn't understand that command. Here's what I can help you with:\n\n"
                    "📋 View patient information (doctors only)\n"
                    "📬 View your messages/feedback\n"
                    "📅 View your appointments\n"
                    "📊 View prediction history\n"
                    "📢 View announcements\n"
                    "👤 View your profile\n"
                    "⚕️ Ask medical questions (e.g., 'What are symptoms of diabetes?')\n\n"
                    "Type 'help' for more information!"
                )
            }