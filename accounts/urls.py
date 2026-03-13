from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('education/', views.education_list, name='education_list'),
    path('education/add/', views.education_add, name='education_add'),
    path('education/<int:pk>/edit/', views.education_edit, name='education_edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='education_delete'),
    path('experience/', views.experience_list, name='experience_list'),
    path('experience/add/', views.experience_add, name='experience_add'),
    path('experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),
    path('skills/', views.skills_manage, name='skills_manage'),
    path('languages/', views.languages_manage, name='languages_manage'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
    path('export-data/', views.export_data, name='export_data'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
