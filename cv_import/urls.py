from django.urls import path
from . import views

urlpatterns = [
    path('', views.import_cv, name='import_cv'),
    path('<int:pk>/review/', views.import_review, name='import_review'),
    path('<int:pk>/to-profile/', views.import_to_profile, name='import_to_profile'),
    path('<int:pk>/delete/', views.import_delete, name='import_delete'),
]
