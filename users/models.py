import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def user_profile_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/profile_images/<filename>
    return f'user_{instance.user.id}/profile_images/{filename}'

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    @property
    def full_name(self):
        return self.get_full_name()


class Profile(models.Model):
    """
    Profile model that extends the User model with additional information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    image = models.ImageField(
        _('profile image'),
        upload_to=user_profile_image_path,
        default='default.jpg',
        blank=True,
        null=True
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )
    address = models.TextField(_('address'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    state = models.CharField(_('state/province'), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    country = models.CharField(_('country'), max_length=100, blank=True, null=True)
    bio = models.TextField(_('bio'), blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f'{self.user.email} Profile'

    def save(self, *args, **kwargs):
        # Delete old file when updating image
        try:
            this = Profile.objects.get(id=self.id)
            if this.image != self.image and this.image != 'default.jpg':
                if os.path.isfile(this.image.path):
                    os.remove(this.image.path)
        except Profile.DoesNotExist:
            pass
            
        super().save(*args, **kwargs)