from django.conf import settings
from django.shortcuts import render, redirect
from .models import Tenant, TenantEmployees, TenantAddress, TenantGeneralInfo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@login_required
def register_tenant(request):
    if request.method == 'POST':
        tenant, created = Tenant.objects.update_or_create(
            owner=request.user,
            defaults={
                'name': request.POST.get('tenant_name'),
                'tenant_logo': request.FILES.get('tenant_logo'),
                'tenant_gst_number': request.POST.get('tenant_gst_number'),
                'email': request.POST.get('tenant_email'),
                'phone': request.POST.get('tenant_phone'),
            }
        )
        TenantAddress.objects.update_or_create(
            tenant=tenant,
            defaults={
                'plot_no': request.POST.get('tenant_plot_no'),
                'address_line_1': request.POST.get('tenant_address_line_1'),
                'address_line_2': request.POST.get('tenant_address_line_2'),
                'city': request.POST.get('tenant_city'),
                'state': request.POST.get('tenant_state'),
                'pincode': request.POST.get('tenant_pincode'),
                'country': request.POST.get('tenant_country'),
            }
        )
        TenantGeneralInfo.objects.update_or_create(
            tenant=tenant,
            defaults={
                'reels_delete_before_days': request.POST.get('tenant_reels_delete_before_days'),
                'program_delete_before_days': request.POST.get('tenant_program_delete_before_days'),
                'production_delete_before_days': request.POST.get('tenant_production_delete_before_days'),
                'purchase_order_delete_before_days': request.POST.get('tenant_purchase_order_delete_before_days'),
                'database_copy': request.POST.get('tenant_database_copy') == 'on',
                'monthly_report': request.POST.get('tenant_monthly_report') == 'on',
            }
        )
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        if created:
            subject = 'Tenant Registration MultiBox'
            html_message = render_to_string('Tenant/tenant_registration_email.html', {'user': user})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = request.user.email
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            messages.success(request, 'Tenant Registered Successfully.')
            messages.info(request, 'An email has been sent to you for the registration details.')
            return redirect('Tenant:register_tenant')
        messages.success(request, 'Tenant Updated Successfully.')
        return redirect('Tenant:register_tenant')
    tenant_address = TenantAddress.objects.filter(tenant__owner=request.user).first()
    tenant_info = Tenant.objects.filter(owner=request.user).values(
        'name', 'tenant_gst_number', 'email', 'email_verified', 'phone', 'phone_verified'
    ).first()
    tenant_general_info = TenantGeneralInfo.objects.filter(tenant__owner=request.user).first()
    context = {
        'tenant_address': tenant_address,
        'tenant_info': tenant_info,
        'tenant_general_info': tenant_general_info
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


@login_required
def tenant_plans(request):
    return render(request, 'Tenant/tenant_plans.html')
