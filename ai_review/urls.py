from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('cv/<int:cv_id>/', views.review_cv, name='review_cv'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
]
