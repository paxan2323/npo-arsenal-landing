"""
URL маршруты для лендинга "Птицелов"
"""
from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('cookies/', views.cookie_policy, name='cookies'),
    path('document/<int:pk>/download/', views.document_download, name='document_download'),
    path('contact/', views.contact_submit, name='contact_submit'),
]
