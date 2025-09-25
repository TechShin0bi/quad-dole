from products.models import Brand
from django.db.models import Count
from django.db.models import Q


class BrandListMixin:
    model = Brand
    context_object_name = 'brands'
    paginate_by = 24

    def get_queryset(self):
        queryset = Brand.objects.annotate(
            product_count=Count('models__product_model', distinct=True)
        )
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )

        min_products = self.request.GET.get('min_products')
        if min_products and min_products.isdigit():
            queryset = queryset.filter(product_count__gte=int(min_products))

        order_by = self.request.GET.get('order_by', 'name')
        if order_by in ['name', '-name', 'product_count', '-product_count']:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context.update({
            'total_brands': queryset.count(),
            'search_query': self.request.GET.get('q', ''),
            'min_products': self.request.GET.get('min_products', ''),
            'is_active': self.request.GET.get('is_active', ''),
            'order_by': self.request.GET.get('order_by', 'name'),
            'order_options': [
                ('name', 'Name (A-Z)'),
                ('-name', 'Name (Z-A)'),
                ('product_count', 'Product Count (Low to High)'),
                ('-product_count', 'Product Count (High to Low)')
            ]
        })
        

        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        context['query_params'] = query_params.urlencode()
        return context

