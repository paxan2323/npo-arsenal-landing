"""
Формы для лендинга "Птицелов"
"""
from django import forms
from .models import ContactRequest


class ContactForm(forms.ModelForm):
    """Форма обратной связи"""
    
    consent = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных',
        error_messages={
            'required': 'Необходимо дать согласие на обработку персональных данных'
        },
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'consent-checkbox',
        })
    )
    
    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'phone', 'company', 'message', 'consent_given']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя *',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email *',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Телефон',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Организация',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Ваше сообщение *',
                'rows': 4,
                'required': True,
            }),
            'consent_given': forms.HiddenInput(),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        # Удаляем все кроме цифр и +
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        return cleaned
    
    def clean(self):
        cleaned_data = super().clean()
        # Если чекбокс согласия отмечен, устанавливаем consent_given = True
        if cleaned_data.get('consent'):
            cleaned_data['consent_given'] = True
        return cleaned_data
