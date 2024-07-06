from django.urls import path
from .views import (register_tenant, inactive_tenant_page)

app_name = 'Tenant'

urlpatterns = [
    path('register_tenant/', register_tenant, name='register_tenant'),
    path('inactive_tenant_page/', inactive_tenant_page, name='inactive_tenant_page'),
]
