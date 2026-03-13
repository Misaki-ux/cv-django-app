from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SearchQuery(models.Model):
    SOURCE_CHOICES = [
        ('google_maps', _('Google Maps')),
        ('pages_jaunes', _('Pages Jaunes')),
        ('linkedin', _('LinkedIn')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries')
    query = models.CharField(_('Search Query'), max_length=200)
    location = models.CharField(_('Location'), max_length=200)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    radius_km = models.FloatField(_('Radius (km)'), default=10.0)
    source = models.CharField(_('Source'), max_length=20, choices=SOURCE_CHOICES, default='google_maps')
    results_count = models.IntegerField(_('Results Count'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Search Query')
        verbose_name_plural = _('Search Queries')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.query} near {self.location}"


class BusinessContact(models.Model):
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_contacts')
    business_name = models.CharField(_('Business Name'), max_length=300)
    business_type = models.CharField(_('Business Type'), max_length=100, blank=True)
    address = models.TextField(_('Address'), blank=True)
    phone = models.CharField(_('Phone'), max_length=50, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    contact_person = models.CharField(_('Contact Person'), max_length=200, blank=True)
    contact_role = models.CharField(_('Contact Role'), max_length=100, blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    source = models.CharField(_('Source'), max_length=50, blank=True)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    rating = models.FloatField(_('Rating'), null=True, blank=True)
    is_saved = models.BooleanField(_('Saved'), default=False)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Business Contact')
        verbose_name_plural = _('Business Contacts')
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name
