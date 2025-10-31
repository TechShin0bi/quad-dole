from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, View

from ..forms.profile import ProfileUpdateForm, UserUpdateForm


class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('users:profile')

        # If invalid, re-render with errors
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = UserUpdateForm
    success_url = 'users:profile'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, 'Votre profil a été mis à jour avec succès!')
        return reverse_lazy(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'profile_form' not in context:
            context['profile_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context
