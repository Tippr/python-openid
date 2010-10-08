
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'djopenid.server.views',
    url(r'^$', 'server'),
    url(r'^xrds/$', 'idpXrds'),
    url(r'^processTrustResult/$', 'processTrustResult'),
    url(r'^users/(?P<username>[^/]+[/]?)$', 'idPage', name='user_page'),
    url(r'^endpoint/$', 'endpoint'),
    url(r'^trust/$', 'trustPage'),
)
