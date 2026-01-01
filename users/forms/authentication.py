from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'votre@email.com'
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'autocomplete': 'current-password'
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Se souvenir de moi',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
    )


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
            'autocomplete': 'new-password',
        }),
        help_text='Le mot de passe doit contenir au moins 8 caractères.',
        min_length=8,
    )

    password2 = forms.CharField(
        label='Confirmation mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password',
        }),
        help_text='Le mot de passe doit contenir au moins 8 caractères.',
        min_length=8,
    )
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        return password1

    
    # def clean_password1(self):
    #     password1 = self.cleaned_data.get('password1')
    #     if len(password1) != 8:
    #         raise forms.ValidationError("Le mot de passe doit contenir exactement 8 caractères.")
    #     if not any(char.isupper() for char in password1):
    #         raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
    #     if not any(char.islower() for char in password1):
    #         raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
    #     if not any(char.isdigit() for char in password1):
    #         raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
    #     return password1

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
