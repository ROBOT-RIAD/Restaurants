import django_filters
from .models import Item




class ItemFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")

    class Meta:
        model = Item
        fields = ['category',]

