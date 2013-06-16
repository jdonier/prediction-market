from django.conf.urls import patterns, url
from django.conf.urls.defaults import *

urlpatterns = patterns('posts.views',
	url(r'^home/$', 'home'),
	url(r'^contact/$', 'contact'),
	url(r'^help/$', 'help'),
	url(r'^about/$', 'about'),
	url(r'^new/$', 'sign_up'),
	url(r'signin/$', 'sign_in', name='signin'),
	url(r'^user/(?P<id_user>\d+)/$', 'user', name='user'),
	url(r'^users/$', 'all_users', name='all_users'),
	url(r'^markets/$', 'all_markets', name='all_markets'),
	url(r'^markets/new$', 'new_market', name='new_market'),
	url(r'^market/(?P<id_market>\d+)/$', 'market'),
	url(r'^market/(?P<id_market>\d+)/delete$', 'delete_market', name='delete_market'),
	url(r'^market/(?P<id_market>\d+)/settle/(?P<yesno>\d+)$', 'settle', name='settle'),
	url(r'^users/(?P<page>\d)$', 'all_users', name='url_liste'),
	url(r'^signout/$', 'sign_out', name='signout'),
	url(r'^user/(?P<id_user>\d+)/delete$', 'delete_user', name='delete_user'),
)