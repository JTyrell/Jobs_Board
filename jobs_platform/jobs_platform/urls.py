from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Core app handles main pages
    path('jobs/', include('jobs.urls')),  # Jobs related features
    path('accounts/', include('accounts.urls')),  # User accounts features
    path('crm/', include('crm.urls')),  # CRM features
    # Django allauth URLs - for authentication
    path('auth/', include('allauth.urls')),
    # Redirect root URL to home page
    path('', RedirectView.as_view(pattern_name='core:home', permanent=False)),
]

# Add static and media URL mappings for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)