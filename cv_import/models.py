from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class ImportedCV(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imported_cvs')
    original_file = models.FileField(_('Original File'), upload_to='cvs/imports/')
    file_name = models.CharField(_('File Name'), max_length=255)
    file_type = models.CharField(_('File Type'), max_length=10)
    extracted_text = models.TextField(_('Extracted Text'), blank=True)
    parsed_data = models.JSONField(_('Parsed Data'), default=dict, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(_('Error Message'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Imported CV')
        verbose_name_plural = _('Imported CVs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} - {self.user.username}"
