from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def admin_required(view_func=None, redirect_url='home'):
    """
    Decorator for views that checks that the user is logged in and is a staff member,
    redirecting to the login page or specified URL if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=None,
        redirect_field_name=None
    )
    
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

class AdminRequiredMixin:
    """
    Mixin to ensure that only admin users can access the view.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')  # or your login URL
        return super().dispatch(request, *args, **kwargs)
