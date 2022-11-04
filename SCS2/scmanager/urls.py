from django.urls import path
from . import views

urlpatterns = [
	#GET
	path('', views.get_auths, name='auths'),
	path('download_client/',views.download_client),
	path('set_token/', views.set_token),
]