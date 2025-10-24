from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'get_cost')
    fields = ('product', 'price', 'quantity', 'get_cost')

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Total'


class OrderStatusHistoryInline(admin.StackedInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at', 'created_by')
    fields = ('status', 'notes', 'created_at', 'created_by')
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'status', 'payment_status', 'created_at', 
        'total_amount', 'view_order_items'
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = (
        'order_number', 'user', 'total_amount', 'tax_amount', 'shipping_cost',
        'created_at', 'updated_at', 'paid_at', 'view_order_items', 'view_status_history'
    )
    fieldsets = (
        ('Informations de commande', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status',
                'total_amount', 'tax_amount', 'shipping_cost',
                'view_order_items', 'view_status_history'
            )
        }),
        ('Informations de livraison et facturation', {
            'fields': (
                'shipping_address', 'billing_address',
                'phone_number', 'email', 'notes'
            )
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [OrderStatusHistoryInline]
    
    def view_order_items(self, obj):
        items = obj.items.all()
        if not items:
            return "Aucun article"
        return format_html(
            '<ul style="margin:0;padding-left:20px;">' +
            ''.join([f'<li>{item}</li>' for item in items]) +
            '</ul>'
        )
    view_order_items.short_description = 'Articles commandés'
    
    def view_status_history(self, obj):
        history = obj.status_history.all().order_by('-created_at')
        if not history:
            return "Aucun historique"
        return format_html(
            '<ul style="margin:0;padding-left:20px;">' +
            ''.join([
                f'<li>{h.get_status_display()} - {h.created_at.strftime("%d/%m/%Y %H:%M")}' +
                (f'<br><em>{h.notes}</em>' if h.notes else '') + '</li>'
                for h in history
            ]) +
            '</ul>'
        )
    view_status_history.short_description = 'Historique des statuts'
    
    def save_model(self, request, obj, form, change):
        # Track status changes
        if change and 'status' in form.changed_data:
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                created_by=request.user,
                notes=f'Changement de statut via l\'admin par {request.user.get_full_name() or request.user.email}'
            )
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_cost')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'price', 'quantity')
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Total'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('order', 'status', 'created_at', 'created_by')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
