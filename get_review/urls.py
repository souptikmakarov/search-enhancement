from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^getTechRadarReviews', views.getTechRadarReviews, name='getTechRadarReviews'),
    url(r'^getYoutubeReviews', views.getYoutubeReviews, name='getYoutubeReviews')
]