from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CV, CVEducation, CVExperience, CVSkill, CVLanguage, CVTemplate


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['title', 'template', 'full_name', 'email', 'phone', 'address', 'summary', 'photo']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class CVEducationForm(forms.ModelForm):
    class Meta:
        model = CVEducation
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CVExperienceForm(forms.ModelForm):
    class Meta:
        model = CVExperience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CVSkillForm(forms.ModelForm):
    class Meta:
        model = CVSkill
        fields = ['name', 'level']


class CVLanguageForm(forms.ModelForm):
    class Meta:
        model = CVLanguage
        fields = ['name', 'proficiency']


class TemplateSelectForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=CVTemplate.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        label=_('Select a Template'),
        empty_label=None,
    )
