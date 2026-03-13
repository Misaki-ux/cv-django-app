from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json
import csv

from .forms import RegisterForm, UserForm, ProfileForm, EducationForm, ExperienceForm, SkillForm, LanguageForm
from .models import UserProfile, Education, Experience, Skill, Language


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
        elif action == 'delete':
            skill_id = request.POST.get('skill_id')
            Skill.objects.filter(pk=skill_id, profile=profile).delete()
            messages.success(request, _('Skill removed.'))
        return redirect('skills_manage')
    form = SkillForm()
    skills = profile.skills.all()
    return render(request, 'accounts/skills.html', {'form': form, 'skills': skills})


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
