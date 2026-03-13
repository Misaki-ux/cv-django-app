import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import AIReview
from cv_builder.models import CV


def build_cv_text(cv):
    parts = []
    parts.append(f"Name: {cv.full_name}")
    parts.append(f"Email: {cv.email}")
    if cv.summary:
        parts.append(f"\nProfessional Summary:\n{cv.summary}")
    if cv.experiences.exists():
        parts.append("\nWork Experience:")
        for exp in cv.experiences.all():
            end = exp.end_date or "Present"
            parts.append(f"- {exp.position} at {exp.company} ({exp.start_date} - {end})")
            if exp.description:
                parts.append(f"  {exp.description}")
    if cv.educations.exists():
        parts.append("\nEducation:")
        for edu in cv.educations.all():
            end = edu.end_date or "Present"
            parts.append(f"- {edu.degree} at {edu.institution} ({edu.start_date} - {end})")
            if edu.field_of_study:
                parts.append(f"  Field: {edu.field_of_study}")
    if cv.skills.exists():
        parts.append("\nSkills:")
        skills = [s.name for s in cv.skills.all()]
        parts.append(", ".join(skills))
    if cv.languages.exists():
        parts.append("\nLanguages:")
        for lang in cv.languages.all():
            parts.append(f"- {lang.name}: {lang.proficiency}")
    return "\n".join(parts)


def get_ai_review_hf(cv_text, api_key=None):
    if not api_key:
        api_key = settings.HUGGINGFACE_API_KEY
    prompt = (
        "Analyze this CV/Resume and provide constructive feedback. "
        "Rate it 1-100 and give specific suggestions.\n\n"
        f"CV Content:\n{cv_text}\n\n"
        "Provide: 1) Overall Score 2) Summary Feedback 3) Experience Feedback "
        "4) Education Feedback 5) Skills Feedback 6) Formatting Tips 7) Top 5 Suggestions"
    )
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
    try:
        response = requests.post(
            api_url, headers=headers,
            json={"inputs": prompt, "parameters": {"max_length": 1000}},
            timeout=30,
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "")
            return str(result)
    except Exception:
        pass
    return generate_local_review(cv_text)


def generate_local_review(cv_text):
    feedback = {
        "overall_score": 0, "summary_feedback": "", "experience_feedback": "",
        "education_feedback": "", "skills_feedback": "", "formatting_feedback": "",
        "suggestions": [],
    }
    score = 50
    suggestions = []
    text_lower = cv_text.lower()

    has_summary = any(kw in text_lower for kw in ["summary", "profile", "objective", "about"])
    if has_summary:
        score += 10
        feedback["summary_feedback"] = str(_("Good - you have a professional summary. Consider making it more specific to your target role."))
    else:
        feedback["summary_feedback"] = str(_("Missing or weak professional summary. Add a compelling 2-3 sentence summary."))
        suggestions.append(str(_("Add a strong professional summary/objective at the top of your CV.")))

    exp_count = text_lower.count("at ") + text_lower.count("company")
    if exp_count > 2:
        score += 15
        feedback["experience_feedback"] = str(_("Good experience section. Use action verbs and quantify achievements."))
    elif exp_count > 0:
        score += 8
        feedback["experience_feedback"] = str(_("Experience section could be stronger. Add more details."))
        suggestions.append(str(_("Use action verbs (managed, developed, implemented) to describe experience.")))
        suggestions.append(str(_("Quantify achievements where possible (e.g., increased sales by 20%).")))
    else:
        feedback["experience_feedback"] = str(_("No work experience detected. Add your work history."))
        suggestions.append(str(_("Add work experience with company names, dates, and descriptions.")))

    edu_keywords = ["education", "degree", "university", "college", "school", "formation"]
    if any(kw in text_lower for kw in edu_keywords):
        score += 10
        feedback["education_feedback"] = str(_("Education section present. Include relevant coursework or honors."))
    else:
        feedback["education_feedback"] = str(_("Education section missing. Add your educational background."))
        suggestions.append(str(_("Add your educational background with institution names and dates.")))

    if "skills" in text_lower or "competenc" in text_lower:
        score += 10
        feedback["skills_feedback"] = str(_("Skills section present. Consider organizing by category."))
    else:
        feedback["skills_feedback"] = str(_("Add a skills section to highlight your key competencies."))
        suggestions.append(str(_("Add a dedicated skills section with both technical and soft skills.")))

    if "@" in cv_text:
        score += 5
    else:
        suggestions.append(str(_("Add your email address for contact purposes.")))
    if any(c.isdigit() for c in cv_text[:500]):
        score += 5

    word_count = len(cv_text.split())
    if 200 < word_count < 800:
        score += 5
        feedback["formatting_feedback"] = str(_("Good CV length. Aim for 1-2 pages."))
    elif word_count < 200:
        feedback["formatting_feedback"] = str(_("Your CV seems too short. Add more detail."))
        suggestions.append(str(_("Expand your CV content - aim for at least 300-500 words.")))
    else:
        feedback["formatting_feedback"] = str(_("Your CV might be too long. Consider condensing."))
        suggestions.append(str(_("Consider condensing your CV to 1-2 pages.")))

    if "language" in text_lower or "langue" in text_lower:
        score += 5
    else:
        suggestions.append(str(_("Add a languages section if you speak multiple languages.")))

    feedback["overall_score"] = min(score, 95)
    feedback["suggestions"] = suggestions[:7]
    return feedback


@login_required
def review_cv(request, cv_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    existing_reviews = AIReview.objects.filter(cv=cv, user=request.user)
    if request.method == "POST":
        cv_text = build_cv_text(cv)
        review = AIReview.objects.create(user=request.user, cv=cv, status="processing")
        try:
            result = get_ai_review_hf(cv_text)
            if isinstance(result, dict):
                review.overall_score = result.get("overall_score", 50)
                review.summary_feedback = result.get("summary_feedback", "")
                review.experience_feedback = result.get("experience_feedback", "")
                review.education_feedback = result.get("education_feedback", "")
                review.skills_feedback = result.get("skills_feedback", "")
                review.formatting_feedback = result.get("formatting_feedback", "")
                review.suggestions = result.get("suggestions", [])
            elif isinstance(result, str):
                review.raw_response = result
                local = generate_local_review(cv_text)
                review.overall_score = local["overall_score"]
                review.summary_feedback = local["summary_feedback"]
                review.experience_feedback = local["experience_feedback"]
                review.education_feedback = local["education_feedback"]
                review.skills_feedback = local["skills_feedback"]
                review.formatting_feedback = local["formatting_feedback"]
                review.suggestions = local["suggestions"]
            review.status = "completed"
            review.save()
            messages.success(request, _("CV review completed!"))
        except Exception as e:
            cv_text = build_cv_text(cv)
            local = generate_local_review(cv_text)
            review.overall_score = local["overall_score"]
            review.summary_feedback = local["summary_feedback"]
            review.experience_feedback = local["experience_feedback"]
            review.education_feedback = local["education_feedback"]
            review.skills_feedback = local["skills_feedback"]
            review.formatting_feedback = local["formatting_feedback"]
            review.suggestions = local["suggestions"]
            review.status = "completed"
            review.save()
            messages.warning(request, _("Used local analysis (AI service unavailable)."))
        return redirect("review_detail", pk=review.pk)
    return render(request, "ai_review/review.html", {"cv": cv, "reviews": existing_reviews})


@login_required
def review_detail(request, pk):
    review = get_object_or_404(AIReview, pk=pk, user=request.user)
    return render(request, "ai_review/review_detail.html", {"review": review})


@login_required
def review_list(request):
    reviews = AIReview.objects.filter(user=request.user)
    return render(request, "ai_review/review_list.html", {"reviews": reviews})
