# swagger.py
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API de Pagos",
        default_version='v1',
        description="Documentación de la API para gestionar clientes, préstamos y pagos.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
