from program.models import Rsvp


def tukuja_nav(request):
    if not request.user.is_authenticated:
        return {}
    return {
        'tukuja_pending_count': Rsvp.objects.filter(status=Rsvp.STATUS_PENDING).count(),
    }
