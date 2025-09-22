from django.contrib import admin
from .models import Brand, Category
from django.utils.html import format_html


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Logo'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20


# Register your models here.
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
