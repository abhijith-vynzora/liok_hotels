from .models import Property

def global_properties(request):
    # This makes 'properties' and 'all_properties' available in EVERY template automatically
    qs = Property.objects.all().order_by('name')
    return {
        'all_properties': qs,
        'properties': qs,
    }