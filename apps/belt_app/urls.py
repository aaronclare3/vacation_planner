from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login$', views.loginpage),
    url(r'^processregister$', views.register),
    url(r'^process_login$', views.processlogin),
    url(r'^logout$', views.logout),
    url(r'^home$', views.home),
    url(r'^removetrip/(?P<num>\d+)$', views.removetrip),
    url(r'^deletetrip/(?P<num>\d+)$', views.deletetrip),
    url(r'^editthis$', views.edittrip),
    url(r'^trips/edit/(?P<num>\d+)$', views.edittriphome),
    url(r'^trips/(?P<tripid>\d+)$', views.tripinfo),
    url(r'^process_create$', views.process_create),
    url(r'^remove/(?P<tripid>\d+)$', views.removeTrip),
    url(r'^create$', views.create_trip),
]

