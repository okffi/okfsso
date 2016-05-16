from django.conf.urls import url
from django.forms import modelform_factory

from oauth2_provider.views.application import ApplicationRegistration
from oauth2_provider.urls import urlpatterns as oauth_urls
from oauth2_provider.models import get_application_model


class LimitedApplicationRegistration(ApplicationRegistration):
    initial = {
        "client_type": get_application_model().CLIENT_CONFIDENTIAL
    }

    def get_form_class(self):
        return modelform_factory(
            get_application_model(),
            fields=('name', 'redirect_uris', 'client_type')
        )

    def form_valid(self, form):
        app = get_application_model()
        form.instance.authorization_grant_type = app.GRANT_AUTHORIZATION_CODE
        return super(LimitedApplicationRegistration, self).form_valid(form)

urlpatterns = (
    url(r'^applications/register/$',
        LimitedApplicationRegistration.as_view(),
        name="register"),
) + oauth_urls
