import requests
import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from admission.models import Student, DoctorPatientRelationship
from .ai import answer_question
from .ai_agent import AIAgent

@login_required
def chatbot_home(request):
    return render(request, 'chatbot.html')

@csrf_exempt
@require_POST
def ask_bot(request):
    data = json.loads(request.body)
    user_message = data.get("message", "")
    user = request.user

    # Try AI agent first for enhanced functionality
    try:
        agent = AIAgent(user)
        agent_result = agent.process_command(user_message)
        
        # Debug: Print the agent result
        print(f"Agent result: {agent_result}")
        
        # If agent handled the request, return the result
        if isinstance(agent_result, dict):
            if agent_result.get("success", False):
                # For successful operations, return the message directly
                return JsonResponse({"reply": agent_result.get("message", "✅ Operation completed successfully.")})
            elif "action" in agent_result:
                # Handle special actions
                if agent_result["action"] == "medical_query":
                    # For medical queries, use the AI answer_question function
                    try:
                        ai_reply = answer_question(user_message, user)
                        if ai_reply and ai_reply.strip():
                            return JsonResponse({"reply": ai_reply})
                        else:
                            return JsonResponse({"reply": "I couldn't generate a response for that medical question. Please try rephrasing or ask about a different topic."})
                    except Exception as e:
                        return JsonResponse({"reply": f"I encountered an error while processing your medical question: {str(e)}. Please try again."})
                else:
                    # For other actions, return the message
                    return JsonResponse({"reply": agent_result.get("message", "I can help with that. What specific information do you need?")})
            else:
                # For unsuccessful operations, return the error message
                return JsonResponse({"reply": agent_result.get("message", "❌ I couldn't process that request. Please try again.")})
    except Exception as e:
        # Log the error for debugging
        print(f"Agent processing error: {str(e)}")
        # Continue with original functionality if agent fails
        pass

    # Load comprehensive project information
    project_info_path = os.path.join(settings.BASE_DIR, 'chatbot', 'project_info.json')
    try:
        with open(project_info_path, 'r', encoding='utf-8') as f:
            project_info = json.load(f)
    except Exception as e:
        return JsonResponse({"reply": f"⚠️ Could not load project information: {str(e)}"})

    # Get user's assigned doctor if they're an authenticated patient
    assigned_doctor = None
    if user.is_authenticated and not user.is_superuser:
        try:
            relationship = DoctorPatientRelationship.objects.get(patient=user, is_active=True)
            assigned_doctor = relationship.doctor
        except DoctorPatientRelationship.DoesNotExist:
            pass

    # Determine user role and permissions (support anonymous users)
    if user.is_authenticated:
        user_role = "doctor" if user.is_superuser else "patient"
        user_permissions = project_info['user_roles'][user_role]['permissions']
    else:
        user_role = "guest"
        user_permissions = []
    
    # Create comprehensive context
    system_context = f"""
You are an AI Assistant for the {project_info['project_name']} - a comprehensive healthcare and hostel management system.

🎯 PROJECT OVERVIEW:
{project_info['description']}

👤 USER INFORMATION:
- Current User: {user.username}
- Role: {user_role.title()}
- Permissions: {', '.join(user_permissions)}
{f"- Assigned Doctor: {assigned_doctor.username if assigned_doctor else 'No doctor assigned'}" if not user.is_superuser else ""}

🏥 AVAILABLE SERVICES:

1. 🫀 PREDICTION ROOM ({project_info['services']['prediction_room']['url']})
   - {project_info['services']['prediction_room']['description']}
   - Features: {', '.join(project_info['services']['prediction_room']['features'])}
   - How to use: {project_info['services']['prediction_room']['how_to_use']}

2. 📊 PREDICTION HISTORY ({project_info['services']['prediction_history']['url']})
   - {project_info['services']['prediction_history']['description']}
   - Features: {', '.join(project_info['services']['prediction_history']['features'])}

3. 📅 APPOINTMENT SYSTEM ({project_info['services']['appointments']['url']})
   - {project_info['services']['appointments']['description']}
   - Features: {', '.join(project_info['services']['appointments']['features'])}
   - How to use: {project_info['services']['appointments']['how_to_use']}

4. 💬 PRIVATE MESSAGING ({project_info['services']['private_messaging']['url']})
   - {project_info['services']['private_messaging']['description']}
   - Features: {', '.join(project_info['services']['private_messaging']['features'])}

5. 🗨️ COMMUNITY CHAT ({project_info['services']['community_chat']['url']})
   - {project_info['services']['community_chat']['description']}
   - Features: {', '.join(project_info['services']['community_chat']['features'])}

6. 💊 MEDICAL STORE ({project_info['services']['medical_store']['url']})
   - {project_info['services']['medical_store']['description']}
   - Features: {', '.join(project_info['services']['medical_store']['features'])}

7. ⏰ MEDICINE TIMETABLE ({project_info['services']['timetable']['url']})
   - {project_info['services']['timetable']['description']}
   - Features: {', '.join(project_info['services']['timetable']['features'])}

8. 👤 USER PROFILE ({project_info['services']['user_profile']['url']})
   - {project_info['services']['user_profile']['description']}
   - Features: {', '.join(project_info['services']['user_profile']['features'])}

🏠 HOSTEL INFORMATION:
- Name: {project_info['hostel_info']['name']}
- Location: {project_info['hostel_info']['location']}
- Address: {project_info['hostel_info']['address']}
- Mess Timings: {project_info['hostel_info']['mess_timings']}
- Gate Close Time: {project_info['hostel_info']['gate_close_time']}
- Warden: {project_info['hostel_info']['warden']}
- Facilities: {', '.join(project_info['hostel_info']['facilities'])}
- Transportation: Bus Stop: {project_info['hostel_info']['nearest_bus_stop']}, Metro: {project_info['hostel_info']['nearest_metro_station']}

🚌 TRANSPORTATION:
- Bus Lines: {', '.join(project_info['hostel_info']['bus_lines'])}
- Nearest Bus Stop: {project_info['hostel_info']['nearest_bus_stop']}
- Nearest Metro: {project_info['hostel_info']['nearest_metro_station']} ({project_info['hostel_info']['metro_line']})

📍 NEARBY LANDMARKS:
{', '.join(project_info['hostel_info']['nearby_landmarks'])}

❓ COMMON QUERIES YOU CAN HELP WITH:
- Prediction: {', '.join(project_info['common_queries']['prediction'])}
- Appointments: {', '.join(project_info['common_queries']['appointments'])}
- Messaging: {', '.join(project_info['common_queries']['messaging'])}
- Hostel: {', '.join(project_info['common_queries']['hostel'])}
- General: {', '.join(project_info['common_queries']['general'])}

🎯 INSTRUCTIONS:
1. Provide helpful, accurate information about all services
2. Guide users on how to use each feature
3. Be specific about user permissions and requirements
4. For appointment issues, check if user has assigned doctor
5. Provide step-by-step instructions when needed
6. Be friendly and professional
7. If user asks about something not in the system, politely explain what's available
8. Always consider the user's role (patient vs doctor) when providing information

💡 Remember: You are the comprehensive AI assistant for this entire healthcare and hostel management system!
"""

    # Try AI answer first (LangChain/HF). If unavailable, fallback to rules.
    try:
        ai_reply = answer_question(user_message, user)
    except Exception as e:
        print(f"AI answer error: {str(e)}")
        ai_reply = None

    if ai_reply and ai_reply.strip():
        response = ai_reply
    else:
        response = generate_ai_response(user_message, system_context, user_role, assigned_doctor)
    
    return JsonResponse({"reply": response})

def generate_ai_response(user_message, system_context, user_role, assigned_doctor):
    """Generate AI response based on user query and context"""
    message_lower = user_message.lower()
    
    # Medical queries - provide helpful information
    medical_keywords = ['medical', 'medicine', 'symptom', 'treat', 'doctor', 'health', 'disease', 'diagnos', 
                       'condition', 'pain', 'therapy', 'medication', 'prescription', 'illness', 'disorder',
                       'injury', 'recovery', 'prevention', 'vaccine', 'immunization', 'allergy', 'infection']
    
    if any(word in message_lower for word in medical_keywords):
        # For medical queries, provide a more detailed response
        return f"""⚕️ **Medical Information Response:**

I understand you have a medical question about "{user_message}". While I can provide general educational information, please remember that I'm not a substitute for professional medical advice.

For personalized medical advice, I recommend:
- Booking an appointment with your assigned doctor using our Appointment System
- Visiting the Prediction Room for health risk assessments
- Sending a private message to your doctor through our messaging system

Would you like help with booking an appointment or contacting your doctor?"""

    # Prediction Room queries
    if any(word in message_lower for word in ['predict', 'prediction', 'disease', 'heart', 'diabetes', 'hypertension', 'kidney']):
        if 'how' in message_lower:
            return """🫀 **Prediction Room Guide:**

1. **Navigate to Prediction Room** from the navbar
2. **Select a disease type:**
   - Heart Disease Risk Assessment
   - Diabetes Risk Prediction  
   - Hypertension Risk Analysis
   - Kidney Disease Risk Evaluation

3. **Fill in the required health parameters** (age, BMI, blood pressure, etc.)
4. **Click "Predict"** to get instant risk assessment
5. **View results** with confidence scores and recommendations

💡 **Tip:** Your predictions are saved in Prediction History for future reference!"""
        
        return """🫀 **Disease Prediction System Available:**

✅ **Heart Disease Risk Assessment**
✅ **Diabetes Risk Prediction**  
✅ **Hypertension Risk Analysis**
✅ **Kidney Disease Risk Evaluation**

Each prediction uses AI models trained on medical data to assess your risk level. Results include confidence scores and are saved to your history.

**Access:** Click "Prediction Room" in the navbar → Select disease type → Fill parameters → Get results!"""

    # Appointment queries
    elif any(word in message_lower for word in ['appointment', 'book', 'schedule', 'doctor']):
        if 'can\'t' in message_lower or 'not working' in message_lower:
            if not assigned_doctor and user_role == 'patient':
                return """❌ **Appointment Issue Identified:**

You don't have an assigned doctor yet. Here's how to fix this:

1. **Contact your administrator** to assign a doctor to your account
2. **Or ask your doctor** to use the "Manage Assignments" feature
3. **Once assigned**, you'll be able to book appointments

🔧 **For Doctors:** Use "Manage Assignments" in the navbar to assign patients."""
            else:
                return """🔧 **Appointment Troubleshooting:**

**If you can't see your doctor:**
1. Check if you have an assigned doctor (you do: {})
2. Try refreshing the page
3. Clear browser cache
4. Contact admin if issue persists

**To book an appointment:**
1. Go to "Book Appointment" 
2. Select date and time
3. Add reason for visit
4. Confirm booking

**Your assigned doctor:** {}""".format(
                    assigned_doctor.username if assigned_doctor else "No doctor assigned",
                    assigned_doctor.username if assigned_doctor else "None"
                )
        
        return """📅 **Appointment System:**

**For Patients:**
1. **Book Appointment** → Select date/time → Add reason → Confirm
2. **View My Appointments** → See all your bookings
3. **Cancel** appointments if needed

**For Doctors:**
1. **Patient Appointments** → View all patient bookings
2. **Manage status** (Pending/Confirmed/Cancelled)
3. **Update appointment details**

**Your Status:** {}""".format(
            f"Assigned to Dr. {assigned_doctor.username}" if assigned_doctor else "No doctor assigned" if user_role == 'patient' else "Doctor account"
        )

    # Messaging queries
    elif any(word in message_lower for word in ['message', 'chat', 'private', 'contact']):
        if 'private' in message_lower:
            return """💬 **Private Messaging System:**

**Features:**
- Send secure messages to your assigned doctor
- Message history tracking
- Read/unread status
- Real-time communication

**How to use:**
1. Click "Private Messages" in navbar
2. Compose new message
3. Send to your assigned doctor

**Your assigned doctor:** {}""".format(
                assigned_doctor.username if assigned_doctor else "No doctor assigned - contact admin"
            )
        
        return """🗨️ **Messaging Options:**

1. **Private Messages** - Secure communication with your assigned doctor
2. **Community Chat** - Interactive chat with all users

**Private Messages:** For personal medical discussions
**Community Chat:** For general discussions and support

**Access:** Both options available in the navbar!"""

    # Hostel queries
    elif any(word in message_lower for word in ['hostel', 'room', 'facilities', 'timing', 'warden']):
        return """🏠 **BCM Postmetric Boys Hostel Information:**

**📍 Location:** Siddapura, Whitefield, Bengaluru, Karnataka, 560066

**⏰ Timings:**
- Mess: Breakfast 7:30-9:00, Lunch 12:30-2:00, Dinner 7:30-9:00
- Gate Close: 10:00 PM (confirm with office)

**👨‍💼 Warden:** Jagadeesh (contact hostel office for details)

**🏠 Facilities:**
- Shared bathrooms, Mess with routine meals
- Common room, Basic furniture (bed, study table)
- Limited parking space, Wi-Fi in common areas

**🚌 Transportation:**
- Bus Stop: Siddapura (4 min walk) - Lines: 327, 327A, 329M, 500-FB, V-500F, 333-G, 304R, 322, 323, 323‑AK
- Metro: Nallur Halli (37 min walk) - Purple Line

**📍 Nearby:** Holiday Inn & Suites, Prestige Laughing Waters, The Farmhouse Kitchen & Bakery, Silicon Pride Apartment, Siddapura Lake"""

    # Medical Store queries
    elif any(word in message_lower for word in ['medicine', 'store', 'pharmacy', 'buy']):
        return """💊 **Medical Store:**

**Features:**
- Browse available medicines
- Add items to cart
- View cart contents
- Medicine inventory management

**How to use:**
1. Navigate to "Medical Store" in navbar
2. Browse available medicines
3. Add desired items to cart
4. View cart and proceed with purchase

**Access:** Available to all logged-in users!"""

    # Profile queries
    elif any(word in message_lower for word in ['profile', 'account', 'settings', 'update']):
        return """👤 **User Profile Management:**

**Features:**
- Update personal details
- Change profile picture
- View account information
- Manage preferences

**How to use:**
1. Click on "Profile" in navbar
2. Update your information
3. Save changes
4. Keep your details current

**Your Role:** {}""".format(user_role.title())

    # Patient registration queries
    elif any(word in message_lower for word in ['register', 'patient', 'new user']):
        if user_role == 'doctor':
            return """🏥 **Patient Registration:**

As a doctor, you can register new patients through the AI assistant!

Just tell me: "Register a new patient" and I'll guide you through the process.

Required information:
- Username
- Email
- First name
- Last name
- Password
- Date of birth
- Gender
- Phone number
- Address

Would you like to register a new patient now?"""
        else:
            return """🏥 **Patient Registration:**

Only doctors can register new patients in the system.

If you need to register as a new patient, please contact the administration or use the registration page."""
    
    # View patients queries
    elif any(word in message_lower for word in ['view', 'see', 'list', 'patients']):
        if user_role == 'doctor':
            return """📋 **View Patients:**

As a doctor, you can view all patients assigned to you.

Just tell me: "View my patients" and I'll show you the list.

You can also:
- View patient details
- Check patient appointments
- See patient prediction history
- Send messages to patients"""
        else:
            return """📋 **Patient Information:**

As a patient, you can view your own information.

To see your details, go to your Profile page."""
    
    # Feedback/message queries
    elif any(word in message_lower for word in ['feedback', 'messages', 'inbox']):
        return """📬 **View Feedback/Messages:**

You can view your messages and feedback.

Just tell me: "View my messages" or "Show me my feedback" and I'll display them for you.

Features:
- Read messages from your doctor
- See message timestamps
- View message subjects"""
    
    # Announcement queries
    elif any(word in message_lower for word in ['announcement', 'news', 'bulletin']):
        if user_role == 'doctor':
            return """📢 **Announcements:**

As a doctor, you can create and view announcements.

Commands available:
- "Create announcement" - Create a new announcement for all patients
- "View announcements" - See recent announcements

Announcements are automatically emailed to all patients."""
        else:
            return """📢 **Announcements:**

You can view recent announcements from your doctors.

Just tell me: "View announcements" to see the latest news and updates."""
    
    # AI Assistant queries
    elif any(word in message_lower for word in ['ai', 'assistant', 'help', 'what can you do']):
        return """🤖 **AI Assistant Capabilities:**

I can help you with:
- 🏥 **Healthcare Services:**
  - Disease predictions (Heart, Diabetes, Hypertension, Kidney)
  - Appointment booking and management  
  - Private messaging and community chat
  - Health tracking and monitoring
  - **Patient registration (for doctors)**
  - **View patient information (for doctors)**
  - **View feedback/messages**
  - **Create announcements (for doctors)**

- 🏠 **Hostel Services:**
  - Hostel information and facilities
  - Transportation details
  - Timings and contact information

- 💊 **Additional Features:**
  - Medical store access
  - Community chat
  - Profile management
  - Prediction history

**Your Role:** {} | **Assigned Doctor:** {}

**Try asking me to "View my patients", "Create announcement", or "View my profile"**""".format(
            user_role.title(),
            assigned_doctor.username if assigned_doctor else "None assigned"
        )
    
    # General help
    elif any(word in message_lower for word in ['help', 'what can you do', 'services', 'features']):
        return """🤖 **I'm your AI Assistant for the Chronic Care AI System!**

**I can help you with:**

🏥 **Healthcare Services:**
- Disease prediction (Heart, Diabetes, Hypertension, Kidney)
- Appointment booking and management  
- Private messaging and community chat
- Health tracking and monitoring
- **Patient registration (for doctors)**
- **View patient information (for doctors)**
- **View feedback/messages**
- **Create announcements (for doctors)**

🏠 **Hostel Services:**
- Hostel information and facilities
- Transportation details
- Timings and contact information

💊 **Additional Features:**
- Medical store access
- Community chat
- Profile management
- Prediction history

**Your Role:** {} | **Assigned Doctor:** {}

**Just ask me about any service or feature you need help with!**""".format(
            user_role.title(),
            assigned_doctor.username if assigned_doctor else "None assigned"
        )

    # Default response
    else:
        return """🤖 **I'm here to help!**

I can assist you with:
- 🩸 Disease predictions and health assessments
- 📅 Appointment booking and management  
- 💬 Private messaging and community chat
- 🏠 Hostel information and facilities
- 💊 Medical store access
- 👤 Profile management
- **🏥 Patient registration (for doctors)**
- **📋 View patient information (for doctors)**
- **📬 View feedback/messages**
- **📢 Create announcements (for doctors)**

**Your Role:** {} | **Status:** {}

What would you like to know about? Just ask!""".format(
            user_role.title(),
            f"Assigned to Dr. {assigned_doctor.username}" if assigned_doctor else "No doctor assigned" if user_role == 'patient' else "Doctor account"
        )


# New view for handling specific AI agent actions
@csrf_exempt
@login_required
@require_POST
def ai_agent_action(request):
    """Handle specific AI agent actions like patient registration"""
    data = json.loads(request.body)
    action = data.get("action", "")
    payload = data.get("payload", {})
    user = request.user
    
    # Only doctors can perform these actions
    if not user.is_superuser:
        return JsonResponse({"success": False, "message": "Only doctors can perform this action"})
    
    agent = AIAgent(user)
    
    if action == "register_patient":
        result = agent.register_patient(payload)
        return JsonResponse(result)
    elif action == "view_patients":
        result = agent.view_patients(payload)
        return JsonResponse(result)
    elif action == "assign_doctor":
        patient_id = payload.get("patient_id")
        doctor_id = payload.get("doctor_id")
        result = agent.assign_doctor_to_patient(patient_id, doctor_id)
        return JsonResponse(result)
    elif action == "create_announcement":
        title = payload.get("title", "")
        content = payload.get("content", "")
        result = agent.create_announcement(title, content)
        return JsonResponse(result)
    elif action == "view_announcements":
        result = agent.view_announcements()
        return JsonResponse(result)
    else:
        return JsonResponse({"success": False, "message": "Unknown action"})