import io
import os
import json
import re
from urllib.parse import urljoin, urlparse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.db import transaction
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
from weasyprint import HTML

from .models import CV, CVTemplate, CVEducation, CVExperience, CVSkill, CVLanguage
from .forms import CVForm, CVEducationForm, CVExperienceForm, CVSkillForm, CVLanguageForm
from .suggestions import get_skill_suggestions
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
            'avatar': '' if profile.photo else profile.avatar,
        }
        form = CVForm(initial=initial)

    return render(request, 'cv_builder/cv_create.html', {
        'form': form,
        'template': template,
        'profile': profile,
        'avatar_choices': UserProfile.AVATAR_CHOICES,
    })


@login_required
def cv_edit(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    profile, _profile_created = UserProfile.objects.get_or_create(user=request.user)
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
        'skill_groups': [(_('Savoir-faire'), cv.hard_skills), (_('Savoir-être'), cv.soft_skills)],
        'skill_suggestions': get_skill_suggestions(cv),
        'templates': CVTemplate.objects.filter(is_active=True),
        'avatar_choices': UserProfile.AVATAR_CHOICES,
        'avatar_fallback_photo': cv.photo or profile.photo,
        'avatar_fallback_path': profile.avatar,
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
@require_POST
def cv_apply_skill_suggestions(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    suggestions = get_skill_suggestions(cv)['items']
    added = 0
    for suggestion in suggestions:
        _, created = CVSkill.objects.get_or_create(
            cv=cv,
            name=suggestion['name'],
            defaults={
                'category': suggestion['category'],
                'level': 3,
                'order': cv.skills.count(),
            },
        )
        added += int(created)
    if added:
        messages.success(request, _('Added %(count)s suggested skills to your CV.') % {'count': added})
    else:
        messages.info(request, _('All suggested skills are already on your CV.'))
    return redirect('cv_edit', pk=cv.pk)


def _allowed_social_profile_url(value):
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError:
        return False
    host = (parsed.hostname or '').casefold().rstrip('.')
    allowed_hosts = ('linkedin.com', 'facebook.com', 'fb.com')
    allowed_host = any(host == domain or host.endswith('.' + domain) for domain in allowed_hosts)
    if (parsed.scheme != 'https' or not allowed_host or parsed.username or parsed.password
            or (port is not None and port != 443)):
        return False
    if host.endswith('linkedin.com'):
        return parsed.path.startswith(('/in/', '/pub/'))
    return bool(parsed.path.strip('/')) and not parsed.path.startswith(('/login', '/share', '/groups'))


def _read_public_social_profile(url):
    """Read only publicly accessible LinkedIn/Facebook profile metadata."""
    current_url = url
    response = None
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CVBuilderProfileImport/1.0)'}
    try:
        for _ in range(4):
            if not _allowed_social_profile_url(current_url):
                return None
            response = requests.get(current_url, headers=headers, timeout=12, stream=True, allow_redirects=False)
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get('Location')
                response.close()
                if not location:
                    return None
                current_url = urljoin(current_url, location)
                continue
            if response.status_code != 200:
                return None
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > 2_000_000:
                return None
            chunks = []
            total = 0
            for chunk in response.iter_content(65536):
                total += len(chunk)
                if total > 2_000_000:
                    return None
                chunks.append(chunk)
            return b''.join(chunks)
    except (requests.RequestException, ValueError):
        return None
    finally:
        if response is not None:
            response.close()
    return None


def _extract_social_profile(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {'name': '', 'job_title': '', 'company': '', 'summary': '', 'education': '', 'skills': []}
    for key, attribute in (('title', 'og:title'), ('summary', 'og:description')):
        tag = soup.find('meta', attrs={'property': attribute})
        if tag and tag.get('content'):
            result[key] = tag['content'].strip()
    if not result['summary']:
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            result['summary'] = (description.get('content') or '').strip()

    entities = []
    def collect_entities(value):
        if isinstance(value, list):
            for item in value:
                collect_entities(item)
        elif isinstance(value, dict):
            entities.append(value)
            if isinstance(value.get('@graph'), list):
                collect_entities(value['@graph'])

    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        try:
            collect_entities(json.loads(script.string or script.get_text()))
        except (json.JSONDecodeError, TypeError):
            continue

    for entity in entities:
        if not result['name'] and entity.get('name'):
            result['name'] = str(entity['name']).strip()
        if not result['job_title'] and entity.get('jobTitle'):
            result['job_title'] = str(entity['jobTitle']).strip()
        if not result['summary'] and entity.get('description'):
            result['summary'] = str(entity['description']).strip()
        employer = entity.get('worksFor')
        if not result['company'] and employer:
            if isinstance(employer, list):
                employer = employer[0] if employer else {}
            result['company'] = employer.get('name', '') if isinstance(employer, dict) else str(employer)
        alumni = entity.get('alumniOf')
        if not result['education'] and alumni:
            if isinstance(alumni, list):
                alumni = alumni[0] if alumni else {}
            result['education'] = alumni.get('name', '') if isinstance(alumni, dict) else str(alumni)
        if not result['skills'] and entity.get('knowsAbout'):
            values = entity['knowsAbout']
            if not isinstance(values, list):
                values = [values]
            result['skills'] = [str(value.get('name', value) if isinstance(value, dict) else value).strip() for value in values]

    if not result['name'] and result['title']:
        title_name = result['title'].split('|')[0].split('–')[0].split(' - ')[0].strip()
        if title_name.casefold() not in {'linkedin', 'facebook', 'meta'}:
            result['name'] = title_name
    if result['title'] and (not result['job_title'] or not result['company']):
        title_body = result['title'].split('|')[0].strip()
        if result['name'] and title_body.startswith(result['name']):
            title_body = title_body[len(result['name']):].strip(' ,–-')
        role_match = re.search(r'(.+?)\s+at\s+(.+)$', title_body, re.I)
        if role_match:
            result['job_title'] = result['job_title'] or role_match.group(1).strip()
            result['company'] = result['company'] or role_match.group(2).strip()
    if result['summary'] and any(marker in result['summary'].casefold() for marker in (
        'view this profile on linkedin', 'sign in to linkedin', 'log in to facebook',
    )):
        result['summary'] = ''
    if not result['skills']:
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            result['skills'] = [item.strip() for item in keywords['content'].split(',')]
    result['skills'] = [skill for skill in result['skills'] if skill][:20]
    return result


@login_required
@require_POST
def cv_import_public_profile(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    profile_url = (request.POST.get('profile_url') or '').strip()
    if len(profile_url) > 1000 or not _allowed_social_profile_url(profile_url):
        messages.error(request, _('Enter a public LinkedIn or Facebook profile URL.'))
        return redirect('cv_edit', pk=cv.pk)

    html = _read_public_social_profile(profile_url)
    if not html:
        messages.error(request, _('This profile could not be read publicly. Sign-in protected profiles cannot be imported.'))
        return redirect('cv_edit', pk=cv.pk)
    data = _extract_social_profile(html)
    changed = []
    if data['name'] and not cv.full_name:
        cv.full_name = data['name'][:200]
        changed.append('full_name')
    if data['job_title'] and not cv.target_job_title:
        cv.target_job_title = data['job_title'][:200]
        changed.append('target_job_title')
    if data['summary'] and not cv.summary:
        cv.summary = data['summary'][:10000]
        changed.append('summary')
    if changed:
        cv.save(update_fields=changed + ['updated_at'])

    if data['job_title'] and data['company'] and not cv.experiences.exists():
        CVExperience.objects.create(
            cv=cv,
            position=data['job_title'][:200],
            company=data['company'][:200],
            start_date='',
            order=0,
        )
    if data['education'] and not cv.educations.exists():
        CVEducation.objects.create(
            cv=cv,
            institution=data['education'][:200],
            degree=str(_('Studies')),
            start_date='',
            order=0,
        )
    existing_skills = {name.casefold() for name in cv.skills.values_list('name', flat=True)}
    added_skills = 0
    for skill_name in data['skills']:
        if skill_name.casefold() not in existing_skills:
            CVSkill.objects.create(cv=cv, name=skill_name[:100], category='hard', order=cv.skills.count())
            existing_skills.add(skill_name.casefold())
            added_skills += 1

    messages.success(request, _('Imported public profile details. Review them in the CV editor and fill in any missing dates.'))
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
@xframe_options_sameorigin
def cv_preview(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    response = HttpResponse(_render_canvas_document(cv, request), content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-store, max-age=0'
    return response


@login_required
def cv_canvas_edit(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    return render(request, 'cv_builder/cv_canvas_edit.html', {
        'cv': cv,
        'templates': CVTemplate.objects.filter(is_active=True),
    })


@login_required
@require_POST
def cv_save_canvas(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': _('Invalid canvas data.')}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({'ok': False, 'error': _('Invalid canvas data.')}, status=400)

    text = payload.get('text', {})
    text_blocks = payload.get('text_blocks', [])
    section_order = payload.get('section_order', [])
    elements = payload.get('elements', [])
    sidebar_side = payload.get('sidebar_side', 'left')
    try:
        font_scale = max(0.8, min(1.4, float(payload.get('font_scale', 1))))
        sidebar_width = max(20, min(50, int(payload.get('sidebar_width', cv.custom_sidebar_width or 35))))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': _('Invalid size setting.')}, status=400)
    if not isinstance(text, dict) or len(text) > 100 or any(
        not str(key).isdigit() or not isinstance(value, str) or len(value) > 2000
        for key, value in text.items()
    ):
        return JsonResponse({'ok': False, 'error': _('Invalid text content.')}, status=400)
    if not isinstance(text_blocks, list) or len(text_blocks) > 12 or any(
        not isinstance(value, str) or len(value) > 1000 for value in text_blocks
    ):
        return JsonResponse({'ok': False, 'error': _('Invalid custom text blocks.')}, status=400)
    if not isinstance(section_order, list) or len(section_order) > 30 or any(
        not isinstance(value, str) or len(value) > 60 for value in section_order
    ):
        return JsonResponse({'ok': False, 'error': _('Invalid section order.')}, status=400)
    if sidebar_side not in {'left', 'right'}:
        return JsonResponse({'ok': False, 'error': _('Invalid sidebar position.')}, status=400)
    if not isinstance(elements, list) or len(elements) > 100:
        return JsonResponse({'ok': False, 'error': _('Invalid custom elements.')}, status=400)

    primary_color = payload.get('primary_color', cv.custom_primary_color)
    secondary_color = payload.get('secondary_color', cv.custom_secondary_color)
    color_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
    for color in (primary_color, secondary_color):
        if color and not color_pattern.fullmatch(str(color)):
            return JsonResponse({'ok': False, 'error': _('Invalid color value.')}, status=400)
    safe_elements = []
    for element in elements:
        if not isinstance(element, dict) or element.get('type') not in {'text', 'rect', 'line'}:
            return JsonResponse({'ok': False, 'error': _('Invalid custom elements.')}, status=400)
        try:
            coords = {key: float(element.get(key, 0)) for key in ('x', 'y', 'width', 'height')}
        except (TypeError, ValueError):
            return JsonResponse({'ok': False, 'error': _('Invalid custom elements.')}, status=400)
        value = element.get('text', '')
        color = element.get('color', '#2563eb')
        fill_color = element.get('fillColor', '#dbeafe')
        fill_enabled = element.get('fillEnabled', False)
        try:
            border_width = int(element.get('borderWidth', 2))
        except (TypeError, ValueError):
            return JsonResponse({'ok': False, 'error': _('Invalid custom elements.')}, status=400)
        if (any(value < 0 or value > 1 for value in coords.values())
                or not isinstance(value, str) or len(value) > 500
                or not color_pattern.fullmatch(str(color))
                or not color_pattern.fullmatch(str(fill_color)) or not isinstance(fill_enabled, bool)
                or border_width < 0 or border_width > 8):
            return JsonResponse({'ok': False, 'error': _('Invalid custom elements.')}, status=400)
        safe_elements.append({
            **coords, 'type': element['type'], 'text': value, 'color': color,
            'fillColor': fill_color, 'fillEnabled': fill_enabled, 'borderWidth': border_width,
        })

    template_id = payload.get('template_id')
    template_changed = False
    if template_id:
        try:
            template_id = int(template_id)
        except (TypeError, ValueError):
            return JsonResponse({'ok': False, 'error': _('Choose an available template.')}, status=400)
        template = CVTemplate.objects.filter(pk=template_id, is_active=True).first()
        if template is None:
            return JsonResponse({'ok': False, 'error': _('Choose an available template.')}, status=400)
        template_changed = template.pk != cv.template_id
        cv.template = template

    cv.canvas_state = {
        'text': {} if template_changed else {str(key): value for key, value in text.items()},
        'text_blocks': text_blocks,
        'section_order': [] if template_changed else section_order,
        'font_scale': font_scale,
        'sidebar_side': sidebar_side,
        'elements': safe_elements,
    }
    cv.custom_sidebar_width = sidebar_width
    cv.custom_primary_color = primary_color or ''
    cv.custom_secondary_color = secondary_color or ''
    cv.save(update_fields=[
        'canvas_state', 'custom_sidebar_width', 'custom_primary_color',
        'custom_secondary_color', 'template', 'updated_at',
    ])
    return JsonResponse({'ok': True})


def _render_canvas_document(cv, request):
    template_name = f'cv_builder/templates_pdf/{cv.template.slug}.html' if cv.template else 'cv_builder/templates_pdf/modern.html'
    html = render_to_string(template_name, {'cv': cv}, request=request)
    state = cv.canvas_state if isinstance(cv.canvas_state, dict) else {}
    soup = BeautifulSoup(html, 'html.parser')
    headings = soup.select('h2')
    section_labels = {
        'profile': 'summary', 'profil': 'summary', 'contact': 'contact',
        'experience': 'experience', 'expérience': 'experience', 'experiences': 'experience',
        'education': 'education', 'formation': 'education', 'languages': 'languages',
        'langues': 'languages', 'technical skills': 'hard_skills', 'savoir-faire': 'hard_skills',
        'hard skills': 'hard_skills', 'soft skills': 'soft_skills', 'savoir-être': 'soft_skills',
    }
    for heading in headings:
        label = ' '.join(heading.get_text(' ', strip=True).casefold().split())
        heading['data-canvas-section'] = section_labels.get(label, re.sub(r'[^a-z0-9_-]+', '-', label).strip('-')[:60])

    order = state.get('section_order', [])
    rank = {key: index for index, key in enumerate(order)} if isinstance(order, list) else {}
    section_parents = soup.find_all(
        lambda tag: getattr(tag, 'name', None) and tag.find_all('h2', recursive=False)
    )
    for parent in section_parents:
        groups = []
        leading = []
        current = None
        for child in list(parent.contents):
            if getattr(child, 'name', None) == 'h2':
                current = [child]
                groups.append(current)
            elif current is None:
                leading.append(child)
            else:
                current.append(child)
        if not groups:
            continue
        for node in list(parent.contents):
            node.extract()
        for node in leading:
            parent.append(node)
        ordered = sorted(
            enumerate(groups),
            key=lambda item: (rank.get(item[1][0].get('data-canvas-section'), len(rank) + item[0]), item[0]),
        )
        for _, group in ordered:
            wrapper = soup.new_tag('section', attrs={'data-section-group': 'true'})
            for node in group:
                wrapper.append(node)
            parent.append(wrapper)

    editable_selector = 'h1, h2, p, .entry-title, .entry-subtitle, .entry-desc, [data-live-field], .lang-item'
    editable_nodes = []
    for element in soup.select(editable_selector):
        if element.find(attrs={'data-live-field': True}):
            continue
        editable_nodes.append(element)
    for index, element in enumerate(editable_nodes):
        element['data-canvas-text-index'] = str(index)
        replacement = state.get('text', {}).get(str(index))
        if isinstance(replacement, str):
            element.clear()
            element.append(NavigableString(replacement))

    scale = state.get('font_scale', 1)
    try:
        scale = max(0.8, min(1.4, float(scale)))
    except (TypeError, ValueError):
        scale = 1
    font_size = re.compile(r'(font-size\s*:\s*)(\d+(?:\.\d+)?)(pt|px|rem|em)', re.IGNORECASE)
    def resize_font(match):
        return f'{match.group(1)}{float(match.group(2)) * scale:g}{match.group(3)}'
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            style_tag.string.replace_with(font_size.sub(resize_font, style_tag.string))
    for element in soup.find_all(style=True):
        element['style'] = font_size.sub(resize_font, element['style'])
    sidebar = soup.select_one('.sidebar')
    main_column = soup.select_one('.main')
    if state.get('sidebar_side') == 'right' and sidebar is not None and main_column is not None:
        sidebar.extract()
        main_column.insert_after(sidebar)
    body = soup.body or soup
    overlay = soup.new_tag('div', attrs={'class': 'canvas-elements'})
    overlay['style'] = 'position:absolute;left:0;top:0;width:210mm;height:297mm;pointer-events:none;overflow:hidden;z-index:10;'
    for element in state.get('elements', [])[:100] if isinstance(state.get('elements', []), list) else []:
        try:
            x, y, width, height = (float(element.get(key, 0)) for key in ('x', 'y', 'width', 'height'))
        except (AttributeError, TypeError, ValueError):
            continue
        color = element.get('color', '#2563eb')
        border_width = max(0, min(8, int(element.get('borderWidth', 2))))
        style = f'position:absolute;left:{x * 100:.3f}%;top:{y * 100:.3f}%;width:{width * 100:.3f}%;height:{height * 100:.3f}%;color:{color};'
        if element.get('fillEnabled') and re.fullmatch(r'#[0-9a-fA-F]{6}', str(element.get('fillColor', ''))):
            style += f'background-color:{element["fillColor"]};'
        if element.get('type') == 'text':
            node = soup.new_tag('div', attrs={'style': style + 'font-size:10pt;white-space:pre-wrap;'})
            node.string = str(element.get('text', ''))[:500]
        elif element.get('type') == 'line':
            node = soup.new_tag('div', attrs={'style': style + f'height:0;border-top:{border_width}px solid currentColor;'})
        elif element.get('type') == 'rect':
            node = soup.new_tag('div', attrs={'style': style + f'border:{border_width}px solid currentColor;'})
        else:
            continue
        overlay.append(node)
    if overlay.contents:
        body.append(overlay)
    for index, value in enumerate(state.get('text_blocks', [])[:12] if isinstance(state.get('text_blocks', []), list) else []):
        section = soup.new_tag('section', attrs={'class': 'canvas-custom-block', 'data-canvas-custom-block': str(index)})
        heading = soup.new_tag('h2')
        heading.string = str(_('Additional information'))
        paragraph = soup.new_tag('p')
        paragraph.string = value
        section.append(heading)
        section.append(paragraph)
        target = soup.select_one('.main, .content') or body
        target.append(section)
    return str(soup)


@login_required
def cv_download_pdf(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    html_string = _render_canvas_document(cv, request)

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
        target_job_title=original.target_job_title,
        email=original.email,
        phone=original.phone,
        address=original.address,
        summary=original.summary,
        photo=original.photo,
        avatar=original.avatar,
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
        CVSkill.objects.create(cv=new_cv, name=skill.name, level=skill.level, category=skill.category, order=skill.order)
    for lang in original.languages.all():
        CVLanguage.objects.create(cv=new_cv, name=lang.name, proficiency=lang.proficiency, order=lang.order)

    messages.success(request, _('CV duplicated!'))
    return redirect('cv_edit', pk=new_cv.pk)
