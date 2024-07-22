from django.urls import path
from .views import (register_tenant, tenant_plans)

app_name = 'Tenant'

urlpatterns = [
    path('register_tenant/', register_tenant, name='register_tenant'),
    path('tenant_plans/', tenant_plans, name='tenant_plans'),
]
