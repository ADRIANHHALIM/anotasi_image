from django import forms

from . models import *

class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-class',
            'placeholder': 'Username',
        })
    )
    number_email = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-class',
            'placeholder': 'Mobile Number or Email',
        })
    )
    password = forms.CharField(
        max_length=15,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-class',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-class',
            'placeholder': 'Last Name',
        })
    )
    peran = forms.ChoiceField(
        choices=[
            ('', 'Select Role'),
            ('0', 'Guest'),
            ('2', 'Annotator'),
            ('3', 'Reviewer'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select', 
        })
    )

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(max_length=15, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
        

