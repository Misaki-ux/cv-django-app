from django.contrib import admin
from .models import SearchQuery, BusinessContact

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "location", "source", "results_count", "created_at"]
    list_filter = ["source"]

@admin.register(BusinessContact)
class BusinessContactAdmin(admin.ModelAdmin):
    list_display = ["business_name", "phone", "email", "source", "is_saved"]
    list_filter = ["source", "is_saved"]
    search_fields = ["business_name", "email", "phone"]
