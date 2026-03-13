from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home, dashboard, set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('set-language/', set_language, name='set_language'),
    path('accounts/', include('accounts.urls')),
    path('cv/', include('cv_builder.urls')),
    path('import/', include('cv_import.urls')),
    path('review/', include('ai_review.urls')),
    path('search/', include('job_search.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
