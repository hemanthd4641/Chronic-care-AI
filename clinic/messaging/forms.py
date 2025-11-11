from django import forms
from django.contrib.auth.models import User
from .models import PrivateMessage, ChatRoomMessage

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['recipient', 'subject', 'message']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter message subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_superuser:
                # Doctor can message any patient
                self.fields['recipient'].queryset = User.objects.filter(is_superuser=False)
            else:
                # Patient can only message doctors
                self.fields['recipient'].queryset = User.objects.filter(is_superuser=True)

class ChatRoomMessageForm(forms.ModelForm):
    class Meta:
        model = ChatRoomMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Type your message here...',
                'id': 'chat-message-input'
            }),
        }

