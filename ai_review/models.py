from django.db import models
from django.contrib.auth.models import User
from cv_builder.models import CV
from django.utils.translation import gettext_lazy as _


class AIReview(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_reviews')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='reviews')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    overall_score = models.IntegerField(_('Overall Score'), null=True, blank=True)
    summary_feedback = models.TextField(_('Summary Feedback'), blank=True)
    experience_feedback = models.TextField(_('Experience Feedback'), blank=True)
    education_feedback = models.TextField(_('Education Feedback'), blank=True)
    skills_feedback = models.TextField(_('Skills Feedback'), blank=True)
    formatting_feedback = models.TextField(_('Formatting Feedback'), blank=True)
    suggestions = models.JSONField(_('Suggestions'), default=list, blank=True)
    raw_response = models.TextField(_('Raw AI Response'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('AI Review')
        verbose_name_plural = _('AI Reviews')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.cv.title} - {self.user.username}"
