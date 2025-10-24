from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory


@receiver(post_save, sender=Order)
def create_initial_status_history(sender, instance, created, **kwargs):
    """
    Create initial status history when a new order is created
    """
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes='Commande créée',
            created_by=instance.user
        )


@receiver(pre_save, sender=Order)
def track_status_changes(sender, instance, **kwargs):
    """
    Track status changes and create history entries
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status has changed, create history entry
                OrderStatusHistory.objects.create(
                    order=instance,
                    status=instance.status,
                    notes=f'Statut changé de {old_instance.get_status_display()} à {instance.get_status_display()}',
                    created_by=instance.user
                )
                
                # Additional actions based on status change
                if instance.status == 'cancelled':
                    # Restore product stock if order is cancelled
                    for item in instance.items.all():
                        if item.product:
                            item.product.stock += item.quantity
                            item.product.save()
                            
                elif instance.status == 'paid' and not instance.paid_at:
                    instance.paid_at = timezone.now()
                    
        except Order.DoesNotExist:
            pass
