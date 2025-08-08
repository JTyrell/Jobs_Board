from django.contrib import admin
from django.urls import path, include
from allauth.account.views import password_reset_from_key

def password_reset_from_key_compat(request, uidb64, key, **kwargs):
    """Backward-compat wrapper mapping uidb64 param name to uidb36 expected by Allauth <0.61"""
    return password_reset_from_key(request, uidb36=uidb64, key=key, **kwargs)
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Core app handles main pages
    path('jobs/', include('jobs.urls')),  # Jobs related features
    path('accounts/', include('accounts.urls')),  # User accounts features
                    path('crm/', include('crm.urls')),  # CRM features
                path('resume/', include('resume_processor.urls')),  # Resume processing
                # Django allauth URLs - for authentication
    # Alias for backward compatibility with older allauth route names
    path('auth/password/reset/key/<uidb64>-<key>/', password_reset_from_key_compat, name='account_reset_password_from_key'),

    path('auth/', include('allauth.urls')),
    # Redirect root URL to home page
    path('', RedirectView.as_view(pattern_name='core:home', permanent=False)),
]

# Add static and media URL mappings for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)