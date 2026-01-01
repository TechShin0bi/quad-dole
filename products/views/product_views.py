import logging
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, UpdateView as BaseUpdateView

from products.models import Product , Category , Brand , ProductImage
from products.forms.product_forms import ProductForm , ProductImageFormSet
from products.forms import ProductImageForm
from .base import StaffRequiredMixin
from django.http import Http404

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        
        # Filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)
            
        # Price range filter
        min_price = self.request.GET.get('min_price')
        if min_price and min_price.isdigit():
            queryset = queryset.filter(price__gte=float(min_price))
            
        max_price = self.request.GET.get('max_price')
        if max_price and max_price.isdigit():
            queryset = queryset.filter(price__lte=float(max_price))
            
        # Featured filter
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        # Ordering
        order_by = self.request.GET.get('order_by', '-created_at')
        if order_by in ['price', '-price', 'name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all categories and brands for filters
        categories = Category.objects.all()
        brands = Brand.objects.all()
        
        # Get filter values from request
        search_query = self.request.GET.get('q', '')
        selected_category = self.request.GET.get('category', '')
        selected_brand = self.request.GET.get('brand', '')
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        featured = self.request.GET.get('featured', '')
        order_by = self.request.GET.get('order_by', '-created_at')
        
        # Add filter values to context
        context.update({
            'categories': categories,
            'brands': brands,
            'search_query': search_query,
            'selected_category': selected_category,
            'selected_brand': selected_brand,
            'min_price': min_price,
            'max_price': max_price,
            'featured': featured,
            'order_by': order_by,
            'order_options': [
                ('-created_at', 'Newest First'),
                ('created_at', 'Oldest First'),
                ('name', 'Name (A-Z)'),
                ('-name', 'Name (Z-A)'),
                ('price', 'Price (Low to High)'),
                ('-price', 'Price (High to Low)')
            ]
        })
        
        # Add filter URL for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = query_params.urlencode()
        
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products from the same category, excluding the current product
        if self.object.category:
            related_products = Product.objects.filter(
                category=self.object.category
            ).exclude(id=self.object.id)[:4]
        else:
            related_products = Product.objects.none()
            
        context['related_products'] = related_products
        return context


class ProductImagesView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/manage_images.html'
    form_class = ProductImageForm
    context_object_name = 'product'
    
    def get_success_url(self):
        # Use the product's pk instead of the image list's pk
        return reverse_lazy('products:manage-images', kwargs={'pk': self.kwargs['pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if 'delete_image' in request.POST:
            # Handle image deletion
            image_id = request.POST.get('delete_image')
            try:
                image = self.object.images.get(id=image_id)
                image.delete()
                messages.success(request, 'Image supprimée avec succès.')
            except ProductImage.DoesNotExist:
                messages.error(request, "L'image spécifiée n'existe pas.")
            return redirect(self.get_success_url())
            
        # Handle form submission for new images
        if form.is_valid():
            # The form's save method returns a list of saved images
            saved_images = form.save(commit=False)
            for img in saved_images:
                img.product = self.object
                img.save()
            return self.form_valid(form)
        return self.form_invalid(form)
        
    def form_valid(self, form):
        # Don't try to save the form here as we're handling it in post
        return super().form_valid(form)
            
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def form_valid(self, form):
        try:
            # The form's save method already handles creating ProductImage instances
            form.save(commit=True)
            messages.success(self.request, 'Image(s) ajoutée(s) avec succès.')
        except Exception as e:
            logger.error(f"Error saving product images: {str(e)}")
            messages.error(self.request, 'Une erreur est survenue lors de l\'ajout des images.')
        
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        """Add the product instance to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # This sets the product instance
        return kwargs


# Configure logger
logger = logging.getLogger(__name__)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:product-list")  # fallback

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context["formset"] = ProductImageFormSet()
        context["title"] = "Add Product"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Product created successfully!")
            return redirect(self.object.get_absolute_url())
        else:
            return self.form_invalid(form)


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    def form_valid(self, form):
        self.object = form.save()

        # Save multiple product images
        extra_images = self.request.FILES.getlist("extra_images")
        for img in extra_images:
            ProductImage.objects.create(product=self.object, image=img)

        messages.success(self.request, "Product created successfully!")
        return redirect(self.object.get_absolute_url())


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    def form_valid(self, form):
        self.object = form.save()

        # Add new extra images if uploaded
        extra_images = self.request.FILES.getlist("extra_images")
        for img in extra_images:
            ProductImage.objects.create(product=self.object, image=img)

        messages.success(self.request, "Product updated successfully!")
        return redirect(self.object.get_absolute_url())




class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product-list')
    success_message = "Le produit a été supprimé avec succès."
    context_object_name = 'product'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, "Le produit que vous essayez de supprimer n'existe pas ou a déjà été supprimé.")
            raise

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return redirect(self.success_url)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Http404:
            return redirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            messages.success(request, self.success_message)
            return redirect(success_url)
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de la suppression du produit: {str(e)}")
            return redirect(self.success_url)