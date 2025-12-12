from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DocumentUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload Document',
        help_text='Supported formats: PDF, TXT (Max 10MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.txt'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'txt']:
                raise forms.ValidationError('Only PDF and TXT files are allowed.')
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB.')
        return file

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})