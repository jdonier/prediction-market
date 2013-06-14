from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^posts/', include('posts.urls')),
    # Examples:
    # url(r'^$', 'twitter.views.home', name='home'),
    # url(r'^twitter/', include('twitter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	url(r'', include('django.contrib.auth.urls')),
    # Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)
