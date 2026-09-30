from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
import json
import csv
import re
import unicodedata

from .forms import RegisterForm, UserForm, ProfileForm, EducationForm, ExperienceForm, SkillForm, LanguageForm
from .models import UserProfile, Education, Experience, Skill, Language


def app_information(request):
    return render(request, 'accounts/app_info.html')


@login_required
def terms_acceptance(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.terms_accepted_at:
        return redirect('dashboard')
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('dashboard')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = reverse('dashboard')
    if request.method == 'POST':
        if request.POST.get('accept_terms') != 'yes':
            messages.error(request, _('Please confirm that you have read and accept the Terms of Use.'))
        else:
            profile.terms_accepted_at = timezone.now()
            profile.save(update_fields=['terms_accepted_at', 'updated_at'])
            return redirect(next_url)
    return render(request, 'accounts/terms_acceptance.html', {'next_url': next_url})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                consent_given=True,
                consent_date=timezone.now(),
                preferred_language=request.LANGUAGE_CODE or 'en'
            )
            login(request, user)
            messages.success(request, _('Account created successfully!'))
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    cvs = request.user.cvs.all()[:5]
    reviews = request.user.ai_reviews.all()[:5]
    imports = request.user.imported_cvs.all()[:5]
    searches = request.user.search_queries.all()[:5]
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'cvs': cvs,
        'reviews': reviews,
        'imports': imports,
        'searches': searches,
    })


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def education_list(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    educations = profile.educations.all()
    return render(request, 'accounts/education_list.html', {'educations': educations})


@login_required
def education_add(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.profile = profile
            edu.save()
            messages.success(request, _('Education added successfully!'))
            return redirect('education_list')
    else:
        form = EducationForm()
    return render(request, 'accounts/education_form.html', {'form': form, 'title': _('Add Education')})


@login_required
def education_edit(request, pk):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=edu)
        if form.is_valid():
            form.save()
            messages.success(request, _('Education updated successfully!'))
            return redirect('education_list')
    else:
        form = EducationForm(instance=edu)
    return render(request, 'accounts/education_form.html', {'form': form, 'title': _('Edit Education')})


@login_required
def education_delete(request, pk):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    if request.method == 'POST':
        edu.delete()
        messages.success(request, _('Education deleted.'))
    return redirect('education_list')


@login_required
def experience_list(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    experiences = profile.experiences.all()
    return render(request, 'accounts/experience_list.html', {'experiences': experiences})


@login_required
def experience_add(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.profile = profile
            exp.save()
            messages.success(request, _('Experience added successfully!'))
            return redirect('experience_list')
    else:
        form = ExperienceForm()
    return render(request, 'accounts/experience_form.html', {'form': form, 'title': _('Add Experience')})


@login_required
def experience_edit(request, pk):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, _('Experience updated successfully!'))
            return redirect('experience_list')
    else:
        form = ExperienceForm(instance=exp)
    return render(request, 'accounts/experience_form.html', {'form': form, 'title': _('Edit Experience')})


@login_required
def experience_delete(request, pk):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    if request.method == 'POST':
        exp.delete()
        messages.success(request, _('Experience deleted.'))
    return redirect('experience_list')


@login_required
def skills_manage(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = SkillForm(request.POST)
            if form.is_valid():
                skill = form.save(commit=False)
                skill.profile = profile
                skill.save()
                messages.success(request, _('Skill added!'))
        elif action == 'edit':
            skill = get_object_or_404(Skill, pk=request.POST.get('skill_id'), profile=profile)
            form = SkillForm(request.POST, instance=skill)
            if form.is_valid():
                form.save()
                messages.success(request, _('Skill updated!'))
            else:
                for error in form.errors.get('name', []):
                    messages.error(request, error)
        elif action == 'delete':
            skill_id = request.POST.get('skill_id')
            Skill.objects.filter(pk=skill_id, profile=profile).delete()
            messages.success(request, _('Skill removed.'))
        return redirect('skills_manage')
    form = SkillForm()
    skills = list(profile.skills.all())
    # Older PDF imports could save CID font markers as skill names. Those
    # values cannot be reconstructed reliably, so discard only the corrupt
    # record and keep the rest of the user's skills intact.
    corrupt_skills = []
    for skill in skills:
        if re.search(r'\(cid:\s*\d+\)', skill.name, re.I):
            corrupt_skills.append(skill)
            continue
        cleaned_name = unicodedata.normalize('NFKC', skill.name)
        cleaned_name = re.sub(r'[‡ƒ†…‚„�\ufffd\u0000\ue000-\uf8ff€]+', ' ', cleaned_name)
        cleaned_name = re.sub(r'\.{2,}', ' ', cleaned_name)
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip(' .,:;–—-')
        if not cleaned_name or not any(char.isalpha() for char in cleaned_name):
            corrupt_skills.append(skill)
        elif cleaned_name != skill.name:
            skill.name = cleaned_name
            skill.save(update_fields=['name'])
    for skill in corrupt_skills:
        skill.delete()
    skill_forms = [(skill, SkillForm(instance=skill)) for skill in skills]
    return render(request, 'accounts/skills.html', {
        'form': form,
        'skills': skills,
        'skill_forms': skill_forms,
    })


@login_required
def languages_manage(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = LanguageForm(request.POST)
            if form.is_valid():
                lang = form.save(commit=False)
                lang.profile = profile
                lang.save()
                messages.success(request, _('Language added!'))
        elif action == 'delete':
            lang_id = request.POST.get('lang_id')
            Language.objects.filter(pk=lang_id, profile=profile).delete()
            messages.success(request, _('Language removed.'))
        return redirect('languages_manage')
    form = LanguageForm()
    languages = profile.languages.all()
    return render(request, 'accounts/languages.html', {'form': form, 'languages': languages})


@login_required
def privacy_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/privacy.html', {'profile': profile})


@login_required
def export_data(request):
    """RGPD: Export all user data"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    data = {
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'profile': {
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'country': profile.country,
            'summary': profile.summary,
            'avatar': profile.avatar,
        },
        'educations': list(profile.educations.values()),
        'experiences': list(profile.experiences.values()),
        'skills': list(profile.skills.values()),
        'languages': list(profile.languages.values()),
    }
    response = HttpResponse(
        json.dumps(data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="my_data_export.json"'
    return response


@login_required
@require_POST
def delete_account(request):
    """RGPD: Delete user account and all associated data"""
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, _('Your account and all data have been permanently deleted.'))
    return redirect('home')


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


def set_language(request):
    """Switch language"""
    lang = request.GET.get('lang', 'en')
    if lang in ('en', 'fr'):
        from django.utils.translation import activate
        activate(lang)
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', lang)
        if request.user.is_authenticated:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.preferred_language = lang
            profile.save()
    else:
        response = redirect('/')
    return response
