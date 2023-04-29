from django_filters import FilterSet, DateTimeFilter, ModelChoiceFilter, ChoiceFilter
from django.forms import DateTimeInput
from .models import Post, Author, Category, CATEGORY_CHOICES

class PostFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='dateCreation',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )
    author = ModelChoiceFilter(
        queryset = Author.objects.all(),
        label = 'Authors',
        empty_label = 'All'
    )
    categoryType = ChoiceFilter(
        choices = CATEGORY_CHOICES,
        label = 'Category',
        empty_label = 'Any'
    )
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            #'categoryType': ['exact'],
            #'author': ['exact'],
        }