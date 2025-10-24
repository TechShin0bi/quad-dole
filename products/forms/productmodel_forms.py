from django import forms
from ..models import ProductModel

class ProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['name', 'brand', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input border min-h-[48px] mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500'
