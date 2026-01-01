from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Product, ProductModel

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'created_at')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('brand',)
    autocomplete_fields = ('brand',)
    fieldsets = (
        (None, {
            'fields': ('name', 'brand', 'description')
                }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_per_page = 20
    list_display_links = ('name', 'display_image')
    readonly_fields = ('created_at', 'updated_at')
    change_form_template = 'admin/products/brand/change_form.html'
    change_list_template = 'admin/products/brand/change_list.html'
    fieldsets = (
        (None, {
            'fields': ('name', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image)
        return "No Image"
    display_image.short_description = 'Logo'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_per_page = 20
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    change_form_template = 'admin/products/category/change_form.html'
    change_list_template = 'admin/products/category/change_list.html'
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'display_image', 'price', 'status_badge', 'created_at')
    list_filter = ('created_at', 'updated_at', 'category')
    list_editable = ('price',)
    search_fields = ('name', 'category__name', 'sku')
    autocomplete_fields = ('category',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    save_on_top = True
    change_form_template = 'admin/products/product/change_form.html'
    change_list_template = 'admin/products/product/change_list.html'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'price', 'description', 'sku', 'is_active')
        }),
        ('Images', {
            'fields': ('image',),
            'classes': ('wide', 'extrapad'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; height: auto;" />', obj.image)
        return "No Image"
    image_preview.short_description = 'Preview'
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image)
        return "No Image"
    display_image.short_description = 'Image'
    
    def status_badge(self, obj):
        return 'Active'  # Simple status since we don't track availability anymore
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


# Register your models here.
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
