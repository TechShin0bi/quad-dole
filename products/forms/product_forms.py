from django import forms
from ..models import Product, ProductModel , ProductImage
from django.forms import inlineformset_factory, modelformset_factory
        
class ProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['name', 'brand', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm',
                'placeholder': 'Entrez le nom du modèle'
            }),
            'brand': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-red-500 focus:outline-none focus:ring-red-500 sm:text-sm',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm',
                'placeholder': 'Décrivez ce modèle de produit...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                '@change': 'fileChaged',
                'x-ref': 'fileInput'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add common classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                # Default styling for any field not explicitly styled
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm',
                })


class MultiFileInput(forms.ClearableFileInput):
    """Custom file input to support multiple file uploads."""
    allow_multiple_selected = True


class MultiFileInput(forms.ClearableFileInput):
    """Custom file input to support multiple uploads."""
    allow_multiple_selected = True


class ProductForm(forms.ModelForm):
    extra_images = forms.ImageField(
        widget=MultiFileInput(attrs={
            "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
            "multiple": True
        }),
        required=False,
        label="Additional Images"
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'description', 'price', 'sku']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Enter SKU'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'rows': 3,
                'placeholder': 'Enter product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'image': forms.TextInput(attrs={
                'class': 'block w-full rounded-md p-3 border-2 border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Enter image URL'
            }),
        }



class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']


# Inline formset for multiple product images
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,   # show 3 empty image fields by default
    can_delete=True
)