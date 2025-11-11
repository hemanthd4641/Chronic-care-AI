"""
Test script for the chatbot functionality
"""
import os
import sys
import django
import json

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')
django.setup()

from django.contrib.auth.models import User
from chatbot.ai_agent import AIAgent

def test_ai_agent():
    """Test the AI agent functionality"""
    print("🧪 Testing AI Agent Functionality")
    print("=" * 50)
    
    # Create a test doctor user
    try:
        doctor_user = User.objects.get(username='test_doctor')
    except User.DoesNotExist:
        doctor_user = User.objects.create_user(
            username='test_doctor',
            email='doctor@test.com',
            password='testpass123',
            is_superuser=True
        )
        print("✅ Created test doctor user")
    
    # Create a test patient user
    try:
        patient_user = User.objects.get(username='test_patient')
    except User.DoesNotExist:
        patient_user = User.objects.create_user(
            username='test_patient',
            email='patient@test.com',
            password='testpass123'
        )
        print("✅ Created test patient user")
    
    # Test doctor commands
    print("\n👨‍⚕️ Testing Doctor Commands:")
    doctor_agent = AIAgent(doctor_user)
    
    doctor_commands = [
        "help",
        "view profile",
        "view appointments",
        "view prediction history",
        "view announcements",
        "view patients",
        "what are symptoms of diabetes?"
    ]
    
    for command in doctor_commands:
        print(f"\n📝 Command: {command}")
        result = doctor_agent.process_command(command)
        print(f"✅ Response: {result.get('message', 'No message')[:100]}...")
    
    # Test patient commands
    print("\n👤 Testing Patient Commands:")
    patient_agent = AIAgent(patient_user)
    
    patient_commands = [
        "help",
        "view profile",
        "view appointments",
        "view prediction history",
        "view announcements",
        "what are symptoms of heart disease?"
    ]
    
    for command in patient_commands:
        print(f"\n📝 Command: {command}")
        result = patient_agent.process_command(command)
        print(f"✅ Response: {result.get('message', 'No message')[:100]}...")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_ai_agent()