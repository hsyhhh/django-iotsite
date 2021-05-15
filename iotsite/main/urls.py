from django.urls import path, re_path

from . import views

from django.conf.urls import url

urlpatterns = [
	path('signup/', views.signup, name='signup'),
	path('profile/', views.profile, name='profile'),
	path('mydevice/', views.mydevice, name='mydevice'),
	path('clients/delete/<client_id>', views.delete_client, name='delete'),
	path('clients/<client_id>/', views.client, name='client'),
	url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
	url(r'^ajax/validate_email/$', views.validate_email, name='validate_email'),
	path('', views.index, name='index'),
]

