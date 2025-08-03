from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets when they are created
# from jobs_app.api.viewsets import JobViewSet
# from crm_app.api.viewsets import LeadViewSet

router = DefaultRouter()
# router.register(r'jobs', JobViewSet)
# router.register(r'leads', LeadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]