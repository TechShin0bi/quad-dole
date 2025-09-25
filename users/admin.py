# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.utils.translation import gettext_lazy as _
# from .models import User, Profile
# from users.forms import UserChangeForm, UserCreationForm


# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     # The forms to add and change user instances
#     form = UserChangeForm
#     add_form = UserCreationForm
#     inlines = (ProfileInline,)
    
#     # The fields to be used in displaying the User model.
#     list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)
    
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name')}),
#         (_('Permissions'), {
#             'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
    
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
    
#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super().get_inline_instances(request, obj)


# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone_number', 'city', 'country')
#     list_filter = ('city', 'state', 'country')
#     search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
#     raw_id_fields = ('user',)
    
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'image')
#         }),
#         (_('Contact Info'), {
#             'fields': ('phone_number', 'address', 'city', 'state', 'postal_code', 'country')
#         }),
#         (_('Additional Info'), {
#             'fields': ('bio', 'date_of_birth', 'email_verified')
#         }),
#     )
