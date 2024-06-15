from django.conf import settings
from .models import Tenant, TenantEmployees, TenantGeneralInfo


def tenant_logo(request):
    if request.user.is_authenticated:
        try:
            tenant = Tenant.objects.get(owner=request.user)
        except Tenant.DoesNotExist:
            try:
                tenant_employee = TenantEmployees.objects.get(user=request.user)
                tenant = tenant_employee.tenant
            except TenantEmployees.DoesNotExist:
                tenant = None

        if tenant and tenant.tenant_logo:
            return {'tenant_logo_url': settings.MEDIA_URL + str(tenant.tenant_logo)}
    return {'tenant_logo_url': None}


def tenant_premium_check(request):
    if request.user.is_authenticated:
        try:
            tenant = Tenant.objects.get(owner=request.user)
        except Tenant.DoesNotExist:
            try:
                tenant_employee = TenantEmployees.objects.get(user=request.user)
                tenant = tenant_employee.tenant
            except TenantEmployees.DoesNotExist:
                tenant = None

        if tenant:
            tenant_general_info = TenantGeneralInfo.objects.filter(tenant=tenant).first()
            if tenant_general_info and tenant_general_info.premium:
                return {'tenant_premium': True}
    return {'tenant_premium': False}
