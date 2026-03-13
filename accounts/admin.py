from django.contrib import admin
from .models import UserProfile, Education, Experience, Skill, Language

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "city", "country", "preferred_language", "consent_given"]
    list_filter = ["preferred_language", "consent_given", "country"]
    search_fields = ["user__username", "user__email", "phone"]

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["profile", "institution", "degree", "start_date", "end_date"]

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["profile", "company", "position", "start_date", "end_date"]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["profile", "name", "level"]

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["profile", "name", "proficiency"]
