from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, View, FormView
)
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Order, OrderItem, OrderStatusHistory
from products.models import Product
from orders.forms import OrderForm
from cart.cart import Cart
from decimal import Decimal
from utils.utils import send_order_emails

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    # fields = ['shipping_address', 'billing_address', 'phone_number', 'notes']
    template_name = 'orders/order_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context
    
    def form_valid(self, form):
        cart = Cart(self.request)
        if not cart:
            messages.error(self.request, "Votre panier est vide")
            return redirect('cart:cart_detail')
            
        order = form.save(commit=False)
        user = self.request.user
        order.user = user
        order.email = user.email
        
        # Calculate totals
        items = []
        total = 0
        for item in cart:
            product = item['product']
            price = product.price
            quantity = item['quantity']
            subtotal = price * quantity
            total += subtotal
            
            # Create order item
            order_item = OrderItem(
                order=order,
                product=product,
                price=price,
                quantity=quantity
            )
            items.append(order_item)
            
            # Update product stock
            product.save()
        
        # Set order totals
        order.total_amount = total
        order.tax_amount = total * Decimal('0.2')
        order.shipping_cost = Decimal('10.00')
        order.save()
        
        # Save order items
        OrderItem.objects.bulk_create(items)
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Commande créée par le client',
            created_by=order.user
        )
        
        # Clear the cart and verify it was cleared
        cart_cleared = cart.clear()
        if not cart_cleared:
            # If cart wasn't cleared, log the issue
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Failed to clear cart for order #{order.order_number}')
        
        # Force session to save
        self.request.session.modified = True
        
        # ------------------ SEND EMAILS ------------------
        send_order_emails(order)
        
        messages.success(
            self.request,
            f'Confirmation de commande #{order.order_number} : Votre commande a été enregistrée avec succès. '
            f'Un email de confirmation contenant votre facture et les détails de votre commande vous sera envoyé à l\'adresse {user.email}. '
            f'Merci pour votre confiance !'
        )
        return redirect('orders:order_detail', order_number=order.pk)


class OrderSingleProductView(LoginRequiredMixin, FormView):
    template_name = 'orders/order_create.html'
    form_class = OrderForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        
        cart = Cart(self.request)
        cart.add(product=product, quantity=1, override_quantity=True)  # ✅ safer
        context['cart'] = cart
        context['is_single_product'] = True
        return context

    
    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            messages.error(self.request, "Erreur: Le produit n'a pas pu être ajouté au panier")
            return redirect('app_urls:home')

        order = form.save(commit=False)
        user = self.request.user
        order.user = user
        order.email = user.email

        items = []
        total = 0
        for item in cart:
            product = item['product']
            price = product.price
            quantity = item['quantity']
            subtotal = price * quantity
            total += subtotal

            order_item = OrderItem(
                order=order,
                product=product,
                price=price,
                quantity=quantity
            )
            items.append(order_item)
            product.save()


        order.total_amount = total
        order.tax_amount = total * Decimal('0.2')
        order.shipping_cost = Decimal('10.00')
        order.save()
        OrderItem.objects.bulk_create(items)

        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Commande créée par le client',
            created_by=order.user
        )

        cart.clear()
        
        # ------------------ SEND EMAILS ------------------
        send_order_emails(order)
        messages.success(
            self.request,
            f'Confirmation de commande #{order.order_number} : Votre commande a été enregistrée avec succès. '
            f'Un email de confirmation contenant votre facture et les détails de votre commande vous sera envoyé à l\'adresse {user.email}. '
            f'Merci pour votre confiance !'
        )
        return redirect('orders:order_detail', order_number=order.pk)



class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        if order.status not in ['cancelled', 'shipped', 'delivered']:
            order.status = 'cancelled'
            order.save()
            
            # Update product stock
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            
            # Add to status history
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes='Commande annulée par le client',
                created_by=request.user
            )
            
            messages.success(request, 'Votre commande a été annulée avec succès.')
        else:
            messages.error(request, 'Impossible d\'annuler cette commande.')
        
        return redirect('orders:order_detail', order_number=order.pk)


# Admin Views
class AdminOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/admin/order_list.html'
    context_object_name = 'orders'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(Order.STATUS_CHOICES)
        context['current_status'] = self.request.GET.get('status', '')
        return context


class AdminOrderDetailView(UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/admin/order_detail.html'
    context_object_name = 'order'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.all().order_by('-created_at')
        return context


class AdminOrderStatusUpdateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            
            # Update paid_at if status is paid
            if new_status == 'paid' and not order.paid_at:
                order.paid_at = timezone.now()
                
            order.save()
            
            # Add to status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, f'Le statut de la commande a été mis à jour: {dict(Order.STATUS_CHOICES).get(new_status)}')
            
            # Send email notification if needed
            # self.send_status_update_email(order, new_status)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status_display': order.get_status_display(),
                    'updated_at': timezone.now().strftime('%d/%m/%Y %H:%M')
                })
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Statut invalide'})
            
        return redirect('orders:admin_order_detail', pk=order.pk)
    
    def send_status_update_email(self, order, new_status):
        # TODO: Implement email notification
        pass
