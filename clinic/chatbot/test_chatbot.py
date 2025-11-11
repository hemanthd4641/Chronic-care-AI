"""
Test script for the chatbot functionality
"""
import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')
django.setup()

from django.contrib.auth.models import User
from chatbot.ai_agent import AIAgent

def test_ai_agent():
    """Test the AI agent functionality"""
    # Create a test user (doctor)
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
    
    # Create an AI agent instance
    agent = AIAgent(user)
    
    # Test various commands
    test_commands = [
        "help",
        "view profile",
        "view appointments",
        "view prediction history",
        "view announcements",
        "what are symptoms of diabetes?",
        "how to book an appointment?",
        "view patients"  # This should work for doctors
    ]
    
    print("Testing AI Agent Commands:")
    print("=" * 50)
    
    for command in test_commands:
        print(f"\nCommand: {command}")
        result = agent.process_command(command)
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 30)

if __name__ == "__main__":
    test_ai_agent()