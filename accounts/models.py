from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    summary = models.TextField(_('Professional Summary'), blank=True)
    photo = models.ImageField(_('Photo'), upload_to='profile_photos/', blank=True)
    preferred_language = models.CharField(
        _('Preferred Language'),
        max_length=2,
        choices=[('en', _('English')), ('fr', _('French'))],
        default='en'
    )
    # RGPD
    consent_given = models.BooleanField(_('Data Processing Consent'), default=False)
    consent_date = models.DateTimeField(_('Consent Date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Education(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(_('Institution'), max_length=200)
    degree = models.CharField(_('Degree'), max_length=200)
    field_of_study = models.CharField(_('Field of Study'), max_length=200, blank=True)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Education')
        verbose_name_plural = _('Educations')

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(_('Company'), max_length=200)
    position = models.CharField(_('Position'), max_length=200)
    location = models.CharField(_('Location'), max_length=200, blank=True)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)
    current = models.BooleanField(_('Currently Working'), default=False)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Experience')
        verbose_name_plural = _('Experiences')

    def __str__(self):
        return f"{self.position} at {self.company}"


class Skill(models.Model):
    LEVEL_CHOICES = [
        (1, _('Beginner')),
        (2, _('Elementary')),
        (3, _('Intermediate')),
        (4, _('Advanced')),
        (5, _('Expert')),
    ]
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(_('Skill'), max_length=100)
    level = models.IntegerField(_('Level'), choices=LEVEL_CHOICES, default=3)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return self.name


class Language(models.Model):
    PROFICIENCY_CHOICES = [
        ('A1', _('Beginner (A1)')),
        ('A2', _('Elementary (A2)')),
        ('B1', _('Intermediate (B1)')),
        ('B2', _('Upper Intermediate (B2)')),
        ('C1', _('Advanced (C1)')),
        ('C2', _('Proficient (C2)')),
        ('native', _('Native')),
    ]
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(_('Language'), max_length=50)
    proficiency = models.CharField(_('Proficiency'), max_length=10, choices=PROFICIENCY_CHOICES, default='B1')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"
