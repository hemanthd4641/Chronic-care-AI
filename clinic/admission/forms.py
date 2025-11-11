from django import forms
from django.contrib.auth.models import User
from .models import Student  # Make sure to import your Student model

class RegForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter the Password',
            'class': 'form-control'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control'
        })
    )
    dob = forms.DateField(
        widget=forms.SelectDateWidget(attrs={
            'class': 'form-control'
        })
    )
    admission_date = forms.DateField(
        widget=forms.SelectDateWidget(attrs={
            'class': 'form-control'
        })
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-control'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-control'
        })
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number',
            'class': 'form-control'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Address',
            'class': 'form-control',
            'rows': 3
        })
    )
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('user', 'room')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists. Please choose a different username.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email address already exists. Please use a different email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        
        return cleaned_data




class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class updateForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('password1','password2','user',)
