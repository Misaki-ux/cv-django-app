from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CV, CVEducation, CVExperience, CVSkill, CVLanguage, CVTemplate


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['title', 'full_name', 'email', 'phone', 'address', 'summary', 'show_photo', 'photo']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'show_photo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CVDesignForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=CVTemplate.objects.filter(is_active=True),
        label=_('CV Template'),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CV
        fields = ['template', 'custom_primary_color', 'custom_secondary_color', 'custom_sidebar_width']
        widgets = {
            'custom_primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'custom_secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'custom_sidebar_width': forms.NumberInput(attrs={'type': 'range', 'min': 20, 'max': 50, 'step': 1, 'class': 'form-range'}),
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
    level = forms.IntegerField(
        label=_('Level'),
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 5}),
    )

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
