# urls.py
from django.contrib import admin
from django.urls import include, path

from swagger import schema_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Endpoints
    path('payments/', include('payments.urls')),
    path('auth/', include('authentication.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

]
