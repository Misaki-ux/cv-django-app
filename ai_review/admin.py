from django.contrib import admin
from .models import AIReview

@admin.register(AIReview)
class AIReviewAdmin(admin.ModelAdmin):
    list_display = ["cv", "user", "overall_score", "status", "created_at"]
    list_filter = ["status"]
