from .models import Brochure

def brochure_context(request):
    return {
        'site_brochure': Brochure.objects.order_by('-updated_at').first()
    }
