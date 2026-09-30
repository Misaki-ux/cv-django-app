from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from .models import UserProfile


class TermsAcceptanceMiddleware:
    """Require an explicit terms decision before accessing authenticated pages."""

    EXEMPT_PREFIXES = (
        '/accounts/terms/',
        '/accounts/logout/',
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and not request.path.startswith(self.EXEMPT_PREFIXES):
            accepted = UserProfile.objects.filter(user_id=user.pk, terms_accepted_at__isnull=False).exists()
            if not accepted:
                terms_url = reverse('terms_acceptance')
                query = urlencode({'next': request.get_full_path()})
                return redirect(f'{terms_url}?{query}')
        return self.get_response(request)
