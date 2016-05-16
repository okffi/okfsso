from __future__ import unicode_literals

from django.db import models

class AppInfo(models.Model):
    "Apps can share JSON data with each other using this model."
    user = models.ForeignKey('auth.User')
    app = models.ForeignKey('oauth2_provider.Application')
    info = models.TextField()
