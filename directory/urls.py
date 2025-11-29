from django.urls import path
from . import views

app_name = 'directory'
urlpatterns = [
    path('', views.home, name='home'),
    path('person/<int:pk>/', views.person_detail, name='person_detail'),
    path('client-entry/', views.client_entry_page, name='client_entry'),
    path('client-entry/create/', views.client_entry_create, name='client_entry_create'),
    path('apps/', views.apps_list, name='apps_list'),
    path('person/<int:pk>/', views.person_detail, name='person_detail'),
    path("send/", views.send_to_cliq),




]


