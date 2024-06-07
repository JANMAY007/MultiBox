from .models import Tenant, TenantEmployees


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

        if tenant:
            return {'tenant_logo_url': tenant.tenant_logo.url}
    return {'tenant_logo_url': None}
