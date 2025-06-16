import django_filters
from .models import Item

class ItemFilter(django_filters.FilterSet):
    category_name = django_filters.CharFilter(field_name='category__Category_name', lookup_expr='icontains')
    item_name = django_filters.CharFilter(field_name='item_name', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['category_name', 'item_name']

