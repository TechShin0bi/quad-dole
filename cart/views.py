from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormMixin
from django.conf import settings

from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm

class CartAddView(LoginRequiredMixin,View):
    """View for adding products to the cart or updating quantities."""
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product,
                quantity=cd['quantity'],
                override_quantity=cd['override']
            )
        return redirect('cart:cart_detail')


class CartRemoveView(LoginRequiredMixin,View):
    """View for removing products from the cart."""
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart:cart_detail')


class CartDetailView(LoginRequiredMixin, TemplateView):
    """View for displaying the cart contents."""
    template_name = 'cart/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        
        # Check if cart is empty in session
        if not self.request.session.get(settings.CART_SESSION_ID):
            # If cart is empty in session, clear the cart object
            cart.cart = {}
        else:
            # Only process cart items if cart is not empty
            for item in cart:
                item['update_quantity_form'] = CartAddProductForm(initial={
                    'quantity': item['quantity'],
                    'override': True
                })
        
        context['cart'] = cart
        return context
