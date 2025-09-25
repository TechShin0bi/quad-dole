from django import forms
from ..models import Product, ProductModel

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

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'model', 'price', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to form fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500'
        
        # Set the queryset for the model field
        self.fields['model'].queryset = ProductModel.objects.all()
