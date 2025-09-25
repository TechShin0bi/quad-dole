# Import all forms to make them available directly from users.forms
from .authentication import UserLoginForm, UserRegisterForm
from .user_management import UserCreateForm, UserEditForm
from .profile import UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm
from .password_reset import CustomPasswordResetForm, CustomSetPasswordForm

__all__ = [
    'UserLoginForm',
    'UserRegisterForm',
    'UserCreateForm',
    'UserEditForm',
    'UserUpdateForm',
    'ProfileUpdateForm',
    'CustomPasswordChangeForm',
    'CustomPasswordResetForm',
    'CustomSetPasswordForm',
]
