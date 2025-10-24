from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
    error_messages = {
        'invalid_login': 'Please enter a correct email and password.',
        'inactive': 'This account is inactive.',
    }


class UserRegisterForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Entrez votre email'
        }),
        help_text='Obligatoire. Entrez une adresse email valide.'
    )
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Votre prénom'
        })
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Votre nom'
        })
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Créez un mot de passe',
            'autocomplete': 'new-password'
        }),
        help_text='Votre mot de passe doit contenir au moins 8 caractères.'
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        }),
        help_text='Entrez le même mot de passe que précédemment, pour vérification.'
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        error_messages = {
            'email': {
                'unique': 'Un utilisateur avec cet email existe déjà.',
                'required': 'Ce champ est obligatoire.',
                'invalid': 'Veuillez entrer une adresse email valide.'
            },
            'first_name': {
                'required': 'Ce champ est obligatoire.'
            },
            'last_name': {
                'required': 'Ce champ est obligatoire.'
            },
            'password2': {
                'password_mismatch': 'Les deux mots de passe ne correspondent pas.'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show errors after the form has been submitted
        for field in self.fields.values():
            field.error_messages = {'required': 'Ce champ est obligatoire.'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Un utilisateur avec cet email existe déjà.',
                code='unique_email'
            )
        return email
