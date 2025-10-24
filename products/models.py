from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator

class Brand(models.Model):
    """Model representing a brand of ATV/UTV."""
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:brand-detail', kwargs={'pk': self.pk})
    
    @property
    def products(self):
        return Product.objects.filter(model__brand=self)

class ProductModel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du modèle")
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name="Marque"
    )
    description = models.TextField(blank=False, verbose_name="Description")
    image = models.ImageField(
        upload_to='product_models/%Y/%m/%d/',
        blank=False,
        null=False,
        verbose_name="Image du modèle"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modèle de produit"
        verbose_name_plural = "Modèles de produits"
        ordering = ['brand__name', 'name']
        unique_together = ['name', 'brand']

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:productmodel-detail', kwargs={'pk': self.pk})
    

class Category(models.Model):
    """Model representing a product category."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category-detail', kwargs={'pk': self.pk})




class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/images/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f"Image for {self.product.name}"
            
            

class Product(models.Model):
    """Model representing a specific product model."""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, null=True, blank=True, related_name='products')
    model = models.ForeignKey(
        ProductModel,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        related_name='product_model',
        verbose_name="Modèle"
    )
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('products:product-detail', kwargs={'pk': self.pk})

    @property
    def display_name(self):
        """Return the display name in the format 'Brand Name Model Name'."""
        return f"{self.name}"