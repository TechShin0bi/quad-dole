from unicodedata import category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic import TemplateView, ListView
from products.models import Product, Category, Brand, ProductModel
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db.models import Min, Max



# Home view
class HomeView(TemplateView):
    template_name = 'app_urls/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured products
        context['featured_products'] = Product.objects.all().order_by('?')[:8]
        
        # Get featured categories (categories with most products)
        context['featured_categories'] = Category.objects.annotate(
            products_count=Count('products')
        ).filter(products_count__gt=0).order_by('-products_count')[:6]
        
        # Get featured brands (brands with most products)
        context['featured_brands'] = Brand.objects.annotate(
            products_count=Count('models__product_model', distinct=True)
        ).filter(products_count__gt=0).order_by('-products_count')[:8]
        
        # Get latest products
        context['latest_products'] = Product.objects.order_by('-created_at')[:8]
        
        return context

    


class ProductModelListView(ListView):
    model = ProductModel
    context_object_name = 'models'
    paginate_by = 12  # 12 models per page

    def get_template_names(self):
        return ['app_urls/model_list.html']

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        # Filter by brand if brand_id is provided in the URL
        brand_id = self.kwargs.get('brand_id')
        if brand_id:
            queryset = queryset.filter(brand=brand_id)
            
            for model in queryset:
                print("image:",model.image)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    


class ProductModelCategoriesView(DetailView):
    """
    Shows all categories for a given ProductModel.
    """
    model = ProductModel
    pk_url_kwarg = 'model_id' 
    context_object_name = 'product_model'
    template_name = 'app_urls/productmodel_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_model = self.object  # the ProductModel instance

        # Get all categories linked to this model through the many-to-many relationship
        categories = product_model.product_model.all()  # Uses the related_name from the ManyToManyField

        context['categories'] = categories
        context['page_title'] = f"Categories for {product_model.brand.name} {product_model.name}"

        return context
    
    
class ProductCategoryListView(DetailView):
    model = Category
    context_object_name = 'category'
    paginate_by = 12
    template_name = 'app_urls/productcategory_list.html'
    pk_url_kwarg = 'category_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_model  = self.object
        product = Product.objects.filter(category=self.object).filter(category=category_model.id)
        context['products'] = product
        return context
    


class ProductDetailView(DetailView):
    model = Product
    pk_url_kwarg = 'product_id'
    template_name = 'app_urls/product_details.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get main product image and additional images
        main_image = product.image
        additional_images = product.images.all()
        
        # Get related products (products from the same category, excluding current product)
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).order_by('?')[:4]  # Get 4 random related products
        
        # Get product specifications
        specifications = {
            'Catégorie': product.category.name if product.category else 'Non spécifiée',
            'Prix': f"{product.price:.2f} €" if product.price else 'Prix sur demande',
            'Référence': f"REF-{product.id}",
            "Date d'ajout": product.created_at.strftime('%d/%m/%Y')
        }
        
        # Add brand and model if available through category
        if product.category and product.category.models.exists():
            model = product.category.models.first()
            specifications['Marque'] = model.brand.name
            specifications['Modèle'] = model.name
        
        # Add to context
        context.update({
            'main_image': main_image,
            'additional_images': additional_images,
            'related_products': related_products,
            'specifications': specifications,
            'in_stock': True,  # You can replace this with actual stock check
            'stock_quantity': 1,  # You can replace this with actual stock quantity
        })
        
        return context
    