from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            (User.ROLE_TENANT, 'Tenant'),
            (User.ROLE_LANDLORD, 'Landlord'),
        ]
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'password1',
            'password2',
        ]

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if len(first_name.strip()) < 2:
            raise forms.ValidationError("First name must be at least 2 characters.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if len(last_name.strip()) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters.")

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.startswith(('98', '97')):
            raise forms.ValidationError("Enter a valid Nepal phone number.")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")

        return phone


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(
                username=email,
                password=password
            )

            if user is None:
                raise forms.ValidationError("Invalid email or password.")

            cleaned_data['user'] = user

        return cleaned_data


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP'
        })
    )
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
        ]

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if len(first_name.strip()) < 2:
            raise forms.ValidationError("First name must be at least 2 characters.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if len(last_name.strip()) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters.")

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.startswith(('98', '97')):
            raise forms.ValidationError("Enter a valid Nepal phone number.")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")

        return phone