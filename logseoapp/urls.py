#from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from logseoapp.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^(queries|landing_pages)/ranks/$', 'logseoapp.views.get_ranks'),
        url(r'^(queries|landing_pages)/ranks/ajax/get-ranks-datatable/$', 'logseoapp.views.get_ranks_datatable'),

    url(r'^queries/$', 'logseoapp.views.get_queries'),
        url(r'^ajax/get-queries-datatable/$', 'logseoapp.views.get_queries_datatable'),

    url(r'^queries/individual-query/(\d{1,6})/$', 'logseoapp.views.get_phrase'),
    url(r'^landing_pages/$', 'logseoapp.views.get_landing_pages'),
    url(r'^landing_pages/page/(\d{1,6})/$', 'logseoapp.views.get_page'),
    url(r'^search/', include('haystack.urls')),
    url(r'^$', 'logseoapp.views.home', name='home'),
    url(r'^engines/(\w+)/$', 'logseoapp.views.home_engine_detail'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^watchlist/', 'logseoapp.views.get_watchlist'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
