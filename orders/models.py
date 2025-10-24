from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product
from django.core.validators import MinValueValidator


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursée'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    shipping_address = models.TextField()
    billing_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
    
    def __str__(self):
        return f'Commande {self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD + timestamp
            self.order_number = f'ORD{timezone.now().strftime("%Y%m%d%H%M%S")}'
        super().save(*args, **kwargs)
    
    def get_total_cost(self):
        return self.total_amount + self.tax_amount + self.shipping_cost


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.SET_NULL,
        null=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name if self.product else "[Produit supprimé]"}'
    
    def get_cost(self):
        return self.price * self.quantity


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='status_history',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Historique du statut de commande'
        verbose_name_plural = 'Historique des statuts de commande'
    
    def __str__(self):
        return f'{self.order} - {self.get_status_display()} - {self.created_at}'
