from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Education, Experience, Skill, Language


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('Email'))
    first_name = forms.CharField(max_length=30, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last Name'))
    consent = forms.BooleanField(
        required=True,
        label=_('I consent to the processing of my personal data in accordance with the privacy policy (RGPD)')
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'consent']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address', 'city', 'country', 'postal_code',
            'date_of_birth', 'linkedin_url', 'website', 'summary',
            'photo', 'avatar', 'preferred_language'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    def clean_name(self):
        import re
        import unicodedata

        name = unicodedata.normalize('NFKC', self.cleaned_data['name'])
        # Imported PDFs sometimes expose font-glyph IDs instead of real text.
        if re.search(r'\(cid:\s*\d+\)', name, re.I):
            raise forms.ValidationError(_('This skill name came from unreadable PDF text. Please enter it again.'))
        name = re.sub(r'[‡ƒ†…‚„�\ufffd\u0000\ue000-\uf8ff€]+', ' ', name)
        name = re.sub(r'\.{2,}', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip(' .,:;–—-')
        if not name or not any(char.isalpha() for char in name):
            raise forms.ValidationError(_('Enter a readable skill name.'))
        return name

    class Meta:
        model = Skill
        fields = ['name', 'level']


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'proficiency']
