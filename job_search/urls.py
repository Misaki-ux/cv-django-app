from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_search, name='job_search'),
    path('results/<int:pk>/', views.search_results, name='search_results'),
    path('saved/', views.saved_contacts, name='saved_contacts'),
    path('contact/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contact/<int:pk>/toggle-save/', views.toggle_save_contact, name='toggle_save_contact'),
]
