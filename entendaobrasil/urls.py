from django.conf.urls import patterns, include, url
from django.contrib import admin
from core import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'entendaobrasil.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^camara/deputado/(?P<id>[0-9]+)', views.deputado, name='deputado'),
    url(r'^camara/orgao/(?P<sigla>\w+)', views.orgao, name='orgao'),
    url(r'^camara/proposicao/(?P<id>[0-9]+)', views.proposicao, name='proposicao'),
    url(r'^camara', views.camara, name='camara'),

    #url(r'^admin/', include(admin.site.urls)),
)
