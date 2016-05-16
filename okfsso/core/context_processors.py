from django.conf import settings
from django.utils.translation import ugettext as _

def site(request):
    return {
        "SITE_NAME": _(settings.SITE_NAME),
        "SITE_URL": settings.SITE_URL
    }
