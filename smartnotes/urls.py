"""
URL configuration for smartnotes project.
"""
from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OpenAPI schema and documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.notes.urls')),  # Changed to just 'api/' to avoid duplication
]

