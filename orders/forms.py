from django import forms
from .models import Order, OrderStatusHistory


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'billing_address', 'phone_number', 'notes']
        widgets = {
            'shipping_address': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Entrez votre adresse de livraison complète'
            }),
            'billing_address': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Entrez votre adresse de facturation complète'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Votre numéro de téléphone',
                'type': 'tel'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Notes supplémentaires pour la livraison (optionnel)'
            }),
        }
        labels = {
            'shipping_address': 'Adresse de livraison',
            'billing_address': 'Adresse de facturation',
            'phone_number': 'Téléphone',
            'notes': 'Notes supplémentaires',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill addresses if user has them
        if user and user.is_authenticated:
            if user.profile.shipping_address:
                self.fields['shipping_address'].initial = user.profile.shipping_address
            if user.profile.billing_address:
                self.fields['billing_address'].initial = user.profile.billing_address
            if user.profile.phone_number:
                self.fields['phone_number'].initial = user.profile.phone_number


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderStatusHistory
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'status': 'Nouveau statut',
            'notes': 'Notes (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        
        # Limit status choices based on current status
        if order:
            status_choices = list(Order.STATUS_CHOICES)
            current_status = order.status
            
            # Remove current status from choices
            status_choices = [
                (status, label) for status, label in status_choices 
                if status != current_status
            ]
            
            self.fields['status'].choices = [('', '---------')] + status_choices
