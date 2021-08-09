from .models import Category


def get_categories(request):
    categories = Category.objects.filter(parent__isnull=False)
    return {'categories': categories}
