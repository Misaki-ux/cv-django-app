from django.contrib import admin
from .models import ImportedCV

@admin.register(ImportedCV)
class ImportedCVAdmin(admin.ModelAdmin):
    list_display = ["file_name", "user", "file_type", "status", "created_at"]
    list_filter = ["status", "file_type"]
