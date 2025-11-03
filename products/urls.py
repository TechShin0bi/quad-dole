from django.urls import path
from .views.productmodel_views import ProductModelListView, ProductModelDetailView, ProductModelCreateView, ProductModelUpdateView, ProductModelDeleteView
from .views.product_views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView
from .views.brand_views import ClientBrandListView, AdminBrandListView, BrandDetailView, BrandCreateView, BrandUpdateView, BrandDeleteView, BrandModelsProductsView
from .views.category_views import CategoryListView, CategoryDetailView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView, AdminCategoryDetailView

app_name = "products"

urlpatterns = [
    # ProductModel URLs - Public
    path("models/", ProductModelListView.as_view(), name="model-list"),
    
    # Admin ProductModel URLs
    path("productmodels/", ProductModelListView.as_view(), name="productmodel-list"),  # Keep for admin
    path(
        "productmodel/add/",
        ProductModelCreateView.as_view(),
        name="productmodel-create",
    ),
    path(
        "productmodel/<int:pk>/",
        ProductModelDetailView.as_view(),
        name="productmodel-detail",
    ),
    path(
        "productmodel/<int:pk>/update/",
        ProductModelUpdateView.as_view(),
        name="productmodel-update",
    ),
    path(
        "productmodel/<int:pk>/delete/",
        ProductModelDeleteView.as_view(),
        name="productmodel-delete",
    ),
    # Product URLs
    path("products/", ProductListView.as_view(), name="product-list"),
    path("product/add/", ProductCreateView.as_view(), name="product-create"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "product/<int:pk>/update/", ProductUpdateView.as_view(), name="product-update"
    ),
    path(
        "product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"
    ),
    # Brand URLs - Client
    path("brands/", ClientBrandListView.as_view(), name="brand-list"),
    path('brand/<int:id>/models/', BrandModelsProductsView.as_view(), name='brand-models-products'),
    path('brand/<int:pk>/', BrandDetailView.as_view(), name='brand-detail'),
    
    # Brand URLs - Admin
    path('admin/brands/', AdminBrandListView.as_view(), name='admin-brand-list'),
    path('admin/brand/add/', BrandCreateView.as_view(), name='brand-create'),
    path('admin/brand/<int:pk>/update/', BrandUpdateView.as_view(), name='brand-update'),
    path('admin/brand/<int:pk>/delete/', BrandDeleteView.as_view(), name='brand-delete'),
    # Category URLs
    path("admin/categories/<int:pk>/", AdminCategoryDetailView.as_view(), name="admin-category-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("category/add/", CategoryCreateView.as_view(), name="category-create"),
    path(
        "category/<int:pk>/update/",
        CategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "category/<int:pk>/delete/",
        CategoryDeleteView.as_view(),
        name="category-delete",
    ),
]
