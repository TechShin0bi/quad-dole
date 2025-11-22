from django import forms
from products.models import ProductImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class ProductImageForm(forms.ModelForm):
    image = MultipleFileField(required=False)

    class Meta:
        model = ProductImage
        fields = ['image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

    def save(self, commit=True):
        # Handle multiple file uploads
        images = self.cleaned_data.get('image', [])
        saved_images = []
        for img in images:
            product_image = ProductImage(
                product=self.instance,  # Changed from self.instance.product to self.instance
                image=img
            )
            if commit:
                product_image.save()
            saved_images.append(product_image)
        return saved_images