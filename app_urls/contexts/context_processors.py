from products.models import Brand  

def global_brands_data(request):
    brands_by_group = Brand.objects.all().order_by('name')
    return {"all_brands": brands_by_group}
