from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('create/<slug:template_slug>/', views.cv_create, name='cv_create'),
    path('list/', views.cv_list, name='cv_list'),
    path('<int:pk>/edit/', views.cv_edit, name='cv_edit'),
    path('<int:pk>/design/', views.cv_design_edit, name='cv_design_edit'),
    path('<int:pk>/preview/', views.cv_preview, name='cv_preview'),
    path('<int:pk>/canvas/', views.cv_canvas_edit, name='cv_canvas_edit'),
    path('<int:pk>/canvas/save/', views.cv_save_canvas, name='cv_save_canvas'),
    path('<int:pk>/download/', views.cv_download_pdf, name='cv_download_pdf'),
    path('<int:pk>/delete/', views.cv_delete, name='cv_delete'),
    path('<int:pk>/duplicate/', views.cv_duplicate, name='cv_duplicate'),
    path('<int:pk>/add-education/', views.cv_add_education, name='cv_add_education'),
    path('education/<int:item_id>/edit/', views.cv_edit_education, name='cv_edit_education'),
    path('<int:pk>/add-experience/', views.cv_add_experience, name='cv_add_experience'),
    path('<int:pk>/experiences/reorder/', views.cv_reorder_experiences, name='cv_reorder_experiences'),
    path('experience/<int:item_id>/edit/', views.cv_edit_experience, name='cv_edit_experience'),
    path('experience/<int:item_id>/move-to-education/', views.cv_move_experience_to_education, name='cv_move_experience_to_education'),
    path('<int:pk>/add-skill/', views.cv_add_skill, name='cv_add_skill'),
    path('<int:pk>/apply-skill-suggestions/', views.cv_apply_skill_suggestions, name='cv_apply_skill_suggestions'),
    path('<int:pk>/import-public-profile/', views.cv_import_public_profile, name='cv_import_public_profile'),
    path('skill/<int:item_id>/edit/', views.cv_edit_skill, name='cv_edit_skill'),
    path('<int:pk>/add-language/', views.cv_add_language, name='cv_add_language'),
    path('<int:pk>/delete-item/<str:item_type>/<int:item_id>/', views.cv_delete_item, name='cv_delete_item'),
]
