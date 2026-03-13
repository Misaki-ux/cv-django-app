from django.contrib import admin
from .models import CVTemplate, CV, CVEducation, CVExperience, CVSkill, CVLanguage

@admin.register(CVTemplate)
class CVTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "primary_color", "is_active"]
    prepopulated_fields = {"slug": ("name",)}

class CVEducationInline(admin.TabularInline):
    model = CVEducation
    extra = 0

class CVExperienceInline(admin.TabularInline):
    model = CVExperience
    extra = 0

class CVSkillInline(admin.TabularInline):
    model = CVSkill
    extra = 0

class CVLanguageInline(admin.TabularInline):
    model = CVLanguage
    extra = 0

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "template", "updated_at"]
    list_filter = ["template"]
    inlines = [CVEducationInline, CVExperienceInline, CVSkillInline, CVLanguageInline]
