import os
import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import ImportedCV
from accounts.models import UserProfile, Education, Experience, Skill, Language


def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfplumber, fallback to pytesseract for scanned PDFs."""
    import pdfplumber
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass

    if not text.strip():
        try:
            import pytesseract
            from PIL import Image
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except ImportError:
            try:
                import pytesseract
                from PIL import Image
                import pdfplumber as pb
                with pb.open(file_path) as pdf:
                    for page in pdf.pages:
                        img = page.to_image(resolution=300)
                        pil_img = img.original
                        text += pytesseract.image_to_string(pil_img) + "\n"
            except Exception:
                pass
    return text


def extract_text_from_docx(file_path):
    """Extract text from DOCX files."""
    from docx import Document
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def parse_cv_text(text):
    """Parse extracted CV text into structured data."""
    data = {
        'full_name': '',
        'email': '',
        'phone': '',
        'address': '',
        'summary': '',
        'education': [],
        'experience': [],
        'skills': [],
        'languages': [],
    }

    # Extract email
    email_pattern = r'[\w.+-]+@[\w-]+\.[\w.-]+'
    emails = re.findall(email_pattern, text)
    if emails:
        data['email'] = emails[0]

    # Extract phone
    phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
    phones = re.findall(phone_pattern, text)
    if phones:
        data['phone'] = phones[0].strip()

    # Try to extract name from first line
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) < 60 and not re.search(r'[@\d]', first_line):
            data['full_name'] = first_line

    # Extract sections
    section_patterns = {
        'summary': r'(?:summary|profile|objective|about\s*me|profil|r[eé]sum[eé])\s*[:\n](.+?)(?=\n(?:education|experience|skills|languages|formation|exp[eé]rience|comp[eé]tences)|$)',
        'education': r'(?:education|formation|studies|[eé]tudes)\s*[:\n](.+?)(?=\n(?:experience|skills|languages|exp[eé]rience|comp[eé]tences|langues)|$)',
        'experience': r'(?:experience|work\s*experience|exp[eé]rience\s*professionnelle|emploi)\s*[:\n](.+?)(?=\n(?:education|skills|languages|formation|comp[eé]tences|langues)|$)',
        'skills': r'(?:skills|comp[eé]tences|technical\s*skills)\s*[:\n](.+?)(?=\n(?:education|experience|languages|formation|exp[eé]rience|langues)|$)',
        'languages': r'(?:languages|langues|language\s*skills)\s*[:\n](.+?)(?=\n(?:education|experience|skills|formation|exp[eé]rience|comp[eé]tences)|$)',
    }

    text_lower = text.lower()
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            content = text[match.start(1):match.end(1)].strip()
            if section == 'summary':
                data['summary'] = content
            elif section == 'skills':
                skills = re.split(r'[,\n•·\-|]', content)
                data['skills'] = [s.strip() for s in skills if s.strip() and len(s.strip()) < 50]
            elif section == 'languages':
                langs = re.split(r'[,\n•·\-|]', content)
                data['languages'] = [l.strip() for l in langs if l.strip() and len(l.strip()) < 50]

    return data


@login_required
def import_cv(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('cv_file')
        if not uploaded_file:
            messages.error(request, _('Please select a file to upload.'))
            return redirect('import_cv')

        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.pdf', '.docx']:
            messages.error(request, _('Only PDF and DOCX files are supported.'))
            return redirect('import_cv')

        imported = ImportedCV.objects.create(
            user=request.user,
            original_file=uploaded_file,
            file_name=uploaded_file.name,
            file_type=file_ext.replace('.', ''),
            status='processing'
        )

        try:
            file_path = imported.original_file.path
            if file_ext == '.pdf':
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_docx(file_path)

            imported.extracted_text = text
            parsed = parse_cv_text(text)
            imported.parsed_data = parsed
            imported.status = 'completed'
            imported.save()

            messages.success(request, _('CV imported and parsed successfully!'))
            return redirect('import_review', pk=imported.pk)

        except Exception as e:
            imported.status = 'failed'
            imported.error_message = str(e)
            imported.save()
            messages.error(request, _('Error processing CV: ') + str(e))
            return redirect('import_cv')

    imports = ImportedCV.objects.filter(user=request.user)
    return render(request, 'cv_import/import.html', {'imports': imports})


@login_required
def import_review(request, pk):
    imported = get_object_or_404(ImportedCV, pk=pk, user=request.user)
    return render(request, 'cv_import/review.html', {'imported': imported})


@login_required
def import_to_profile(request, pk):
    """Import parsed CV data into user profile."""
    imported = get_object_or_404(ImportedCV, pk=pk, user=request.user)
    data = imported.parsed_data

    if not data:
        messages.error(request, _('No parsed data available.'))
        return redirect('import_review', pk=pk)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Update profile fields
    if data.get('phone') and not profile.phone:
        profile.phone = data['phone']
    if data.get('address') and not profile.address:
        profile.address = data['address']
    if data.get('summary') and not profile.summary:
        profile.summary = data['summary']
    profile.save()

    # Update user name
    if data.get('full_name'):
        parts = data['full_name'].split(' ', 1)
        if not request.user.first_name:
            request.user.first_name = parts[0]
        if len(parts) > 1 and not request.user.last_name:
            request.user.last_name = parts[1]
        if data.get('email') and not request.user.email:
            request.user.email = data['email']
        request.user.save()

    # Import skills
    for skill_name in data.get('skills', []):
        if not Skill.objects.filter(profile=profile, name=skill_name).exists():
            Skill.objects.create(profile=profile, name=skill_name, level=3)

    # Import languages
    for lang_name in data.get('languages', []):
        if not Language.objects.filter(profile=profile, name=lang_name).exists():
            Language.objects.create(profile=profile, name=lang_name, proficiency='B1')

    messages.success(request, _('CV data imported to your profile!'))
    return redirect('profile')


@login_required
def import_delete(request, pk):
    imported = get_object_or_404(ImportedCV, pk=pk, user=request.user)
    if request.method == 'POST':
        if imported.original_file:
            try:
                os.remove(imported.original_file.path)
            except OSError:
                pass
        imported.delete()
        messages.success(request, _('Imported CV deleted.'))
    return redirect('import_cv')
