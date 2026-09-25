from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class CVTemplate(models.Model):
    TEMPLATE_CHOICES = [
        ('modern', _('Modern')),
        ('classic', _('Classic')),
        ('minimalist', _('Minimalist')),
        ('creative', _('Creative')),
        ('executive', _('Executive')),
        ('tech', _('Tech')),
        ('academic', _('Academic')),
        ('elegant', _('Elegant')),
        ('bold', _('Bold')),
        ('simple', _('Simple')),
    ]
    name = models.CharField(_('Template Name'), max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(_('Description'), blank=True)
    preview_image = models.CharField(_('Preview CSS Class'), max_length=100, default='template-preview')
    primary_color = models.CharField(_('Primary Color'), max_length=7, default='#2c3e50')
    secondary_color = models.CharField(_('Secondary Color'), max_length=7, default='#3498db')
    font_family = models.CharField(_('Font Family'), max_length=100, default='Arial, sans-serif')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('CV Template')
        verbose_name_plural = _('CV Templates')

    def __str__(self):
        return self.name


class CV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs')
    template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(_('CV Title'), max_length=200, default=_('My CV'))
    # Personal info override (optional, defaults to profile)
    full_name = models.CharField(_('Full Name'), max_length=200, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    summary = models.TextField(_('Professional Summary'), blank=True)
    photo = models.ImageField(_('Photo'), upload_to='cv_photos/', blank=True)
    show_photo = models.BooleanField(_('Show photo on CV'), default=True)
    # Metadata
    is_public = models.BooleanField(_('Public'), default=False)
    pdf_file = models.FileField(_('PDF File'), upload_to='cvs/pdf/', blank=True)

    # Custom Design Settings
    custom_primary_color = models.CharField(_('Custom Primary Color'), max_length=7, blank=True)
    custom_secondary_color = models.CharField(_('Custom Secondary Color'), max_length=7, blank=True)
    custom_sidebar_width = models.IntegerField(_('Sidebar Width (%)'), default=35)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def main_width(self):
        return 100 - (self.custom_sidebar_width or 35)

    class Meta:
        verbose_name = _('CV')
        verbose_name_plural = _('CVs')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class CVEducation(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(_('Institution'), max_length=200)
    degree = models.CharField(_('Degree'), max_length=200)
    field_of_study = models.CharField(_('Field of Study'), max_length=200, blank=True)
    start_date = models.CharField(_('Start Date'), max_length=20)
    end_date = models.CharField(_('End Date'), max_length=20, blank=True)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class CVExperience(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(_('Company'), max_length=200)
    position = models.CharField(_('Position'), max_length=200)
    location = models.CharField(_('Location'), max_length=200, blank=True)
    start_date = models.CharField(_('Start Date'), max_length=20)
    end_date = models.CharField(_('End Date'), max_length=20, blank=True)
    current = models.BooleanField(_('Current'), default=False)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class CVSkill(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(_('Skill'), max_length=100)
    level = models.IntegerField(_('Level'), default=3)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class CVLanguage(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(_('Language'), max_length=50)
    proficiency = models.CharField(_('Proficiency'), max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
