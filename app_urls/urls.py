from .views import HomeView , ProductModelListView , ProductModelCategoriesView , ProductCategoryListView , ProductDetailView
from django.urls import path

app_name = 'app_urls'  

urlpatterns = [   
    # Home
    path("", HomeView.as_view(), name="home"),
    path("all-brand-model/<int:brand_id>/", ProductModelListView.as_view(), name="brand-model-list"),
    path("all-model-categories/<int:model_id>/", ProductModelCategoriesView.as_view(), name="model-category-list"),
    path("all-products-categories/<int:category_id>/", ProductCategoryListView.as_view(), name="category-detail"),
    path("product-details/<int:product_id>/", ProductDetailView.as_view(), name="product-detail"),

]