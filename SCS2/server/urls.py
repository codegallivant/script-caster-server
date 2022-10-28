from django.urls import path
from . import views

urlpatterns = [
	#POST
	path('auth_client/', views.auth_client),
	path('get_token/', views.get_token),
	path('get_tasks/', views.get_tasks),
	path('send_data/', views.send_data) # combine switch_script into send_data
]