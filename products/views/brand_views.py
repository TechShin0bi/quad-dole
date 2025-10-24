from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404

from products.models import Brand, ProductModel, Product
from products.forms.brand_forms import BrandForm
from products.mixin.mixin import BrandListMixin
from products.views.base import StaffRequiredMixin


# views.py

class AdminBrandListView(BrandListMixin,ListView,):
    model = Brand
    template_name = "products/admin/brand_list.html"


class ClientBrandListView(BrandListMixin,ListView,):
    template_name = "products/client/brand_list.html"

class BrandDetailView(DetailView):
    model = Brand
    template_name = 'products/brand_detail.html'
    context_object_name = 'brand'
    
    def get_queryset(self):
        return Brand.objects.annotate(product_count=Count('products'))


class BrandModelsProductsView(TemplateView):
    template_name = 'products/client/brand_models_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_id = self.kwargs.get('id')

        # Get brand
        brand = get_object_or_404(Brand, id=brand_id)

        # Get models of this brand + annotate with product count
        models_with_counts = (
            ProductModel.objects
            .filter(brand=brand)
            .annotate(product_count=Count('product_model'))  # product_model is the related_name in Product
            .prefetch_related(
                Prefetch(
                    'product_model',
                    queryset=Product.objects.select_related('category'),
                )
            )
        )

        # Get featured products (limit 4)
        featured_products = (
            Product.objects
            .filter(model__brand=brand)
            .select_related('category', 'model__brand')[:4]
        )

        context.update({
            'brand': brand,
            'models_with_counts': models_with_counts,
            'featured_products': featured_products,
        })
        return context


class BrandCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'products/brand_form.html'
    success_url = reverse_lazy('products:brand-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'La marque a été créée avec succès !')
        return super().form_valid(form)


class BrandUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'products/brand_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'La marque a été mise à jour avec succès !')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('products:brand-detail', kwargs={'slug': self.object.slug})


class BrandDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Brand
    template_name = 'products/brand_confirm_delete.html'
    success_url = reverse_lazy('products:brand-list')
    success_message = "La marque a été supprimée avec succès."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
