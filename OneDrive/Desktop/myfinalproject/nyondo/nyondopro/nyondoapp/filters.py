import django_filters
from .models import *


class BateryFilter(django_filters.FilterSet):
    class Meta:
        model = Battery
        fields = ['batery_brand']

class TyreFilter(django_filters.FilterSet):
    class Meta:
        model = Tyre
        fields = ['tyre_brand']