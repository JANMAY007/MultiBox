from django.conf import settings
from django.shortcuts import render, redirect
from .models import Tenant, TenantEmployees, TenantAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@login_required
def register_tenant(request):
    if request.method == 'POST':
        tenant_name = request.POST.get('tenant_name')
        tenant_logo = request.FILES.get('tenant_logo')
        user = request.user
        if Tenant.objects.filter(owner=user).exists():
            messages.info(request, 'You already have a tenant registered.')
            return redirect('Tenant:register_tenant')
        Tenant.objects.create(
            owner=user,
            name=tenant_name,
            tenant_logo=tenant_logo
        )
        # Send email
        subject = 'Tenant Registration MultiBox'
        html_message = render_to_string('Tenant/tenant_registration_email.html', {'user': user})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = user.email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

        messages.success(request, 'Tenant registered successfully.')
        messages.info(request, 'An email has been sent to you for the registration details.')
        return redirect('Corrugation:register_tenant')
    tenant_address = TenantAddress.objects.filter(tenant__owner=request.user).first()
    tenant_info = Tenant.objects.filter(owner=request.user).values('name', 'tenant_gst_number').first()
    context = {
        'tenant_address': tenant_address,
        'tenant_info': tenant_info,
    }
    return render(request, 'Tenant/register_tenant.html', context)


def get_tenant_for_user(request):
    try:
        tenant = Tenant.objects.get(owner=request.user)
        if not tenant.active:
            return redirect('Tenant:inactive_tenant_page')
        return tenant
    except Tenant.DoesNotExist:
        try:
            tenant_employee = TenantEmployees.objects.get(user=request.user)
            tenant = tenant_employee.tenant
            if not tenant.active:
                return redirect('Tenant:inactive_tenant_page')
            return tenant
        except TenantEmployees.DoesNotExist:
            return None


@login_required
def inactive_tenant_page(request):
    return render(request, 'Tenant/inactive_tenant.html')
