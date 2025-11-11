from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from admission.models import Student, DoctorPatientRelationship
from chatbot.ai_agent import AIAgent
import json

class AIAgentTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.doctor = User.objects.create_user(
            username='testdoctor',
            email='doctor@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.patient = User.objects.create_user(
            username='testpatient',
            email='patient@test.com',
            password='testpass123'
        )
        
        # Create student profile for patient
        self.student = Student.objects.create(
            user=self.patient,
            first_name='Test',
            last_name='Patient',
            username='testpatient',
            email='patient@test.com',
            dob='2000-01-01',
            gender='Male',
            phone_number=1234567890,
            address='Test Address',
            password1='testpass123',
            password2='testpass123'
        )
        
        # Create doctor-patient relationship
        self.relationship = DoctorPatientRelationship.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            is_active=True
        )
        
        self.client = Client()
    
    def test_doctor_can_register_patient(self):
        """Test that doctors can register patients"""
        agent = AIAgent(self.doctor)
        patient_data = {
            'username': 'newpatient',
            'email': 'newpatient@test.com',
            'first_name': 'New',
            'last_name': 'Patient',
            'password': 'newpass123',
            'dob': '1990-01-01',
            'gender': 'Female',
            'phone_number': 9876543210,
            'address': 'New Address'
        }
        
        result = agent.register_patient(patient_data)
        self.assertTrue(result['success'])
        self.assertIn('registered successfully', result['message'])
        
        # Verify patient was created
        new_user = User.objects.get(username='newpatient')
        self.assertIsNotNone(new_user)
        self.assertFalse(new_user.is_superuser)
    
    def test_patient_cannot_register_patient(self):
        """Test that patients cannot register patients"""
        agent = AIAgent(self.patient)
        patient_data = {
            'username': 'anotherpatient',
            'email': 'another@test.com',
            'first_name': 'Another',
            'last_name': 'Patient',
            'password': 'another123',
            'dob': '1995-01-01',
            'gender': 'Male',
            'phone_number': 1111111111,
            'address': 'Another Address'
        }
        
        result = agent.register_patient(patient_data)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Only doctors can register patients')
    
    def test_doctor_can_view_patients(self):
        """Test that doctors can view their patients"""
        agent = AIAgent(self.doctor)
        result = agent.view_patients()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['patients'][0]['username'], 'testpatient')
    
    def test_patient_cannot_view_patients(self):
        """Test that patients cannot view patient lists"""
        agent = AIAgent(self.patient)
        result = agent.view_patients()
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Only doctors can view patient information')
    
    def test_user_can_view_own_profile(self):
        """Test that users can view their own profile"""
        # Test doctor profile
        agent = AIAgent(self.doctor)
        result = agent.view_profile()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['profile']['username'], 'testdoctor')
        self.assertTrue(result['profile']['is_doctor'])
        
        # Test patient profile
        agent = AIAgent(self.patient)
        result = agent.view_profile()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['profile']['username'], 'testpatient')
        self.assertFalse(result['profile']['is_doctor'])
        self.assertEqual(result['profile']['first_name'], 'Test')
    
    def test_user_can_view_appointments(self):
        """Test that users can view appointments"""
        agent = AIAgent(self.doctor)
        result = agent.view_appointments()
        
        self.assertTrue(result['success'])
        # Should be empty since we haven't created appointments
        
        agent = AIAgent(self.patient)
        result = agent.view_appointments()
        
        self.assertTrue(result['success'])
        # Should be empty since we haven't created appointments
    
    def test_user_can_view_feedback(self):
        """Test that users can view feedback/messages"""
        agent = AIAgent(self.doctor)
        result = agent.view_feedback()
        
        self.assertTrue(result['success'])
        # Should be empty since we haven't created messages
        
        agent = AIAgent(self.patient)
        result = agent.view_feedback()
        
        self.assertTrue(result['success'])
        # Should be empty since we haven't created messages

class ChatbotViewTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.doctor = User.objects.create_user(
            username='testdoctor',
            email='doctor@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.patient = User.objects.create_user(
            username='testpatient',
            email='patient@test.com',
            password='testpass123'
        )
        
        self.client = Client()
    
    def test_chatbot_home_page(self):
        """Test that chatbot home page loads"""
        # Test without login
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Test with login
        self.client.login(username='testdoctor', password='testpass123')
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chronic Care AI Assistant')
    
    def test_ai_agent_action_requires_login(self):
        """Test that AI agent actions require login"""
        response = self.client.post(
            reverse('ai_agent_action'),
            data=json.dumps({'action': 'view_patients'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_doctor_can_access_ai_agent_actions(self):
        """Test that doctors can access AI agent actions"""
        self.client.login(username='testdoctor', password='testpass123')
        
        response = self.client.post(
            reverse('ai_agent_action'),
            data=json.dumps({'action': 'view_patients'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('success', data)