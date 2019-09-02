from django.conf.urls import url
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^apis/(?P<lat>-?[0-9]\d*(\.\d+)?)/(?P<long>-?[0-9]\d*(\.\d+)?)$', views.apis),
    url(r'^$', views.redirecttohome),
    url(r'^login$', views.loginpage),
    url(r'^processregister$', views.register),
    url(r'^process_login$', views.processlogin),
    url(r'^logout$', views.logout),
    url(r'^home$', views.home),
    url(r'^deletetrip/(?P<num>\d+)$', views.deletetrip),
    url(r'^editthis$', views.edittrip),
    url(r'^trips/edit/(?P<num>\d+)$', views.edittriphome),
    url(r'^trips/(?P<tripid>\d+)$', views.tripinfo),
    url(r'^process_create$', views.process_create),
    url(r'^remove/(?P<tripid>\d+)$', views.removeTrip),
    url(r'^create$', views.create_trip),
]