from django import forms
from .models import Medicine, Order

class MedicineSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search medicines...',
            'id': 'medicine-search'
        })
    )
    
    category = forms.ChoiceField(
        choices=[
            ('', 'All Categories'),
            ('General', 'General'),
            ('Pain Relief', 'Pain Relief'),
            ('Antibiotics', 'Antibiotics'),
            ('Vitamins', 'Vitamins'),
            ('Cardiovascular', 'Cardiovascular'),
            ('Diabetes', 'Diabetes'),
            ('Respiratory', 'Respiratory'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'category-filter'
        })
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your delivery address...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special instructions (optional)...'
            })
        }

class PaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI Payment'),
        ('netbanking', 'Net Banking'),
        ('cod', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'maxlength': '19'
        })
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'maxlength': '5'
        })
    )
    
    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'maxlength': '4'
        })
    )
    
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'yourname@upi'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'card':
            if not cleaned_data.get('card_number'):
                raise forms.ValidationError('Card number is required for card payments.')
            if not cleaned_data.get('expiry_date'):
                raise forms.ValidationError('Expiry date is required for card payments.')
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError('CVV is required for card payments.')
        
        elif payment_method == 'upi':
            if not cleaned_data.get('upi_id'):
                raise forms.ValidationError('UPI ID is required for UPI payments.')
        
        return cleaned_data
