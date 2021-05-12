from django.urls import path

from . import views

from django.conf.urls import url

urlpatterns = [
	path('signup/', views.signup, name='signup'),
	path('profile/', views.profile, name='profile'),
	url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
	url(r'^ajax/validate_email/$', views.validate_email, name='validate_email'),
	path('', views.index, name='index'),
]



