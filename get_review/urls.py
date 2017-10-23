from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^getTechRadarReviews', views.getTechRadarReviews, name='getTechRadarReviews'),
    url(r'^getYoutubeReviews', views.getYoutubeReviews, name='getYoutubeReviews'),
    url(r'^getCnetReviews', views.getCnetReviews, name='getCnetReviews'),
    url(r'^techRadarPostParser', views.techRadarPostParser, name='techRadarPostParser'),
    url(r'^cnetPostParser', views.cnetPostParser, name='cnetPostParser')
]