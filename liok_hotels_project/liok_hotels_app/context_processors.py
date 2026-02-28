from .models import Property

def global_properties(request):
    # This makes 'properties' available in EVERY template automatically
    return {
        'all_properties': Property.objects.all().order_by('name')
    }