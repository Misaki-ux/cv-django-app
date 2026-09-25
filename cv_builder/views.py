import io
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db import transaction
from weasyprint import HTML

from .models import CV, CVTemplate, CVEducation, CVExperience, CVSkill, CVLanguage
from .forms import CVForm, CVEducationForm, CVExperienceForm, CVSkillForm, CVLanguageForm
from accounts.models import UserProfile


@login_required
def template_list(request):
    templates = CVTemplate.objects.filter(is_active=True)
    return render(request, 'cv_builder/template_list.html', {'templates': templates})


@login_required
def cv_create(request, template_slug):
    template = get_object_or_404(CVTemplate, slug=template_slug, is_active=True)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CVForm(request.POST, request.FILES)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            cv.template = template
            cv.save()
            messages.success(request, _('CV created! Now add your details.'))
            return redirect('cv_edit', pk=cv.pk)
    else:
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'summary': profile.summary,
        }
        form = CVForm(initial=initial)

    return render(request, 'cv_builder/cv_create.html', {
        'form': form,
        'template': template,
    })


@login_required
def cv_edit(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CVForm(request.POST, request.FILES, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, _('CV updated!'))
            return redirect('cv_edit', pk=cv.pk)
    else:
        form = CVForm(instance=cv)

    edu_form = CVEducationForm()
    exp_form = CVExperienceForm()
    skill_form = CVSkillForm()
    lang_form = CVLanguageForm()

    return render(request, 'cv_builder/cv_edit.html', {
        'cv': cv,
        'form': form,
        'edu_form': edu_form,
        'exp_form': exp_form,
        'skill_form': skill_form,
        'lang_form': lang_form,
    })


@login_required
def cv_design_edit(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        from .forms import CVDesignForm
        form = CVDesignForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, _('Design settings updated!'))
            return redirect('cv_edit', pk=cv.pk)
    else:
        from .forms import CVDesignForm
        form = CVDesignForm(instance=cv)

    return render(request, 'cv_builder/cv_design_edit.html', {
        'form': form,
        'cv': cv,
        'templates': CVTemplate.objects.filter(is_active=True),
    })


@login_required
def cv_add_education(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CVEducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.cv = cv
            edu.order = cv.educations.count()
            edu.save()
            messages.success(request, _('Education added!'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_add_experience(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CVExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.cv = cv
            exp.order = cv.experiences.count()
            exp.save()
            messages.success(request, _('Experience added!'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_add_skill(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CVSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.cv = cv
            skill.order = cv.skills.count()
            skill.save()
            messages.success(request, _('Skill added!'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_edit_skill(request, item_id):
    skill = get_object_or_404(CVSkill, pk=item_id, cv__user=request.user)
    if request.method == 'POST':
        form = CVSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, _('Skill updated!'))
            return redirect('cv_edit', pk=skill.cv.pk)
    else:
        form = CVSkillForm(instance=skill)
    return render(request, 'cv_builder/cv_edit_skill.html', {'form': form, 'skill': skill})


@login_required
def cv_add_language(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CVLanguageForm(request.POST)
        if form.is_valid():
            lang = form.save(commit=False)
            lang.cv = cv
            lang.order = cv.languages.count()
            lang.save()
            messages.success(request, _('Language added!'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_edit_education(request, item_id):
    edu = get_object_or_404(CVEducation, pk=item_id, cv__user=request.user)
    if request.method == 'POST':
        form = CVEducationForm(request.POST, instance=edu)
        if form.is_valid():
            form.save()
            messages.success(request, _('Education updated!'))
            return redirect('cv_edit', pk=edu.cv.pk)
    else:
        form = CVEducationForm(instance=edu)
    return render(request, 'cv_builder/cv_edit_education.html', {'form': form, 'edu': edu})


@login_required
def cv_edit_experience(request, item_id):
    exp = get_object_or_404(CVExperience, pk=item_id, cv__user=request.user)
    if request.method == 'POST':
        form = CVExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, _('Experience updated!'))
            return redirect('cv_edit', pk=exp.cv.pk)
    else:
        form = CVExperienceForm(instance=exp)
    return render(request, 'cv_builder/cv_edit_experience.html', {'form': form, 'exp': exp})


@login_required
@require_POST
def cv_reorder_experiences(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    try:
        submitted_ids = [int(item_id) for item_id in request.POST.getlist('experience_ids')]
    except (TypeError, ValueError):
        submitted_ids = []
    experiences = list(cv.experiences.all())
    if len(submitted_ids) != len(experiences) or set(submitted_ids) != {item.pk for item in experiences}:
        messages.error(request, _('Could not save the experience order. Please try again.'))
        return redirect('cv_edit', pk=cv.pk)

    by_id = {item.pk: item for item in experiences}
    for order, item_id in enumerate(submitted_ids):
        by_id[item_id].order = order
    CVExperience.objects.bulk_update(experiences, ['order'])
    messages.success(request, _('Experience order updated!'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
@require_POST
def cv_move_experience_to_education(request, item_id):
    experience = get_object_or_404(CVExperience, pk=item_id, cv__user=request.user)
    cv = experience.cv
    description = experience.description
    if experience.location:
        location_line = _('Location: %(location)s') % {'location': experience.location}
        description = f'{location_line}\n{description}'.strip()
    last_education_order = cv.educations.order_by('-order').values_list('order', flat=True).first()
    education_end_date = experience.end_date or ('Present' if experience.current else '')

    with transaction.atomic():
        CVEducation.objects.create(
            cv=cv,
            institution=experience.company or experience.position,
            degree=experience.position or experience.company,
            start_date=experience.start_date,
            end_date=education_end_date,
            description=description,
            order=0 if last_education_order is None else last_education_order + 1,
        )
        experience.delete()
        for order, remaining in enumerate(cv.experiences.all()):
            if remaining.order != order:
                remaining.order = order
                remaining.save(update_fields=['order'])

    messages.success(request, _('Experience moved to Education.'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_delete_item(request, pk, item_type, item_id):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        model_map = {
            'education': CVEducation,
            'experience': CVExperience,
            'skill': CVSkill,
            'language': CVLanguage,
        }
        model = model_map.get(item_type)
        if model:
            model.objects.filter(pk=item_id, cv=cv).delete()
            messages.success(request, _('Item deleted.'))
    return redirect('cv_edit', pk=cv.pk)


@login_required
def cv_preview(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    template_name = f'cv_builder/templates_pdf/{cv.template.slug}.html' if cv.template else 'cv_builder/templates_pdf/modern.html'
    return render(request, template_name, {'cv': cv})


@login_required
def cv_download_pdf(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    template_name = f'cv_builder/templates_pdf/{cv.template.slug}.html' if cv.template else 'cv_builder/templates_pdf/modern.html'
    html_string = render_to_string(template_name, {'cv': cv}, request=request)

    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_bytes = html.write_pdf()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    safe_title = cv.title.replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="{safe_title}.pdf"'
    return response


@login_required
def cv_list(request):
    cvs = CV.objects.filter(user=request.user)
    return render(request, 'cv_builder/cv_list.html', {'cvs': cvs})


@login_required
def cv_delete(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == 'POST':
        cv.delete()
        messages.success(request, _('CV deleted.'))
    return redirect('cv_list')


@login_required
def cv_duplicate(request, pk):
    original = get_object_or_404(CV, pk=pk, user=request.user)
    new_cv = CV.objects.create(
        user=request.user,
        template=original.template,
        title=f"{original.title} (copy)",
        full_name=original.full_name,
        email=original.email,
        phone=original.phone,
        address=original.address,
        summary=original.summary,
        photo=original.photo,
        show_photo=original.show_photo,
    )
    for edu in original.educations.all():
        CVEducation.objects.create(
            cv=new_cv, institution=edu.institution, degree=edu.degree,
            field_of_study=edu.field_of_study, start_date=edu.start_date,
            end_date=edu.end_date, description=edu.description, order=edu.order
        )
    for exp in original.experiences.all():
        CVExperience.objects.create(
            cv=new_cv, company=exp.company, position=exp.position,
            location=exp.location, start_date=exp.start_date,
            end_date=exp.end_date, current=exp.current,
            description=exp.description, order=exp.order
        )
    for skill in original.skills.all():
        CVSkill.objects.create(cv=new_cv, name=skill.name, level=skill.level, order=skill.order)
    for lang in original.languages.all():
        CVLanguage.objects.create(cv=new_cv, name=lang.name, proficiency=lang.proficiency, order=lang.order)

    messages.success(request, _('CV duplicated!'))
    return redirect('cv_edit', pk=new_cv.pk)
