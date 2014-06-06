from django.conf.urls import patterns, include, url
from django.contrib import admin
from core import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'entendaobrasil.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^parlamentares/deputados', views.deputados, name='deputados'),
    url(r'^parlamentares/deputado/(?P<id>[0-9]+)', views.deputado, name='deputado'),
    url(r'^parlamentares/senador/(?P<id>[0-9]+)', views.senador, name='senador'),
    url(r'^parlamentares/senadores', views.senadores, name='senadores'),
    url(r'^parlamentares', views.parlamentares, name='parlamentares'),
    url(r'^partidos/', views.partidos, name='partidos'),

    #url(r'^admin/', include(admin.site.urls)),
)
