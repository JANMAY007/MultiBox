from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Tenant, TenantEmployees, TenantAddress, TenantGeneralInfo, TenantPlan
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
            return redirect('Tenant:register_tenant')
        return tenant
    except Tenant.DoesNotExist:
        try:
            tenant_employee = TenantEmployees.objects.get(user=request.user)
            tenant = tenant_employee.tenant
            if not tenant.active:
                return redirect('Tenant:register_tenant')
            return tenant
        except TenantEmployees.DoesNotExist:
            return None


def plan_info_dict(plan):
    plan_dict = {}
    if plan == 'm_s':
        plan_dict = {
            'stock_management_and_history': False,
            'smart_bulk_reel_addition': False,
            'reel_filtering': False,
            'reel_stocks_and_order_management': False,
            'products_management': True,
            'products_filtering': False,
            'production_line_handling': True,
            'daily_program_management': True,
            'daily_program_sharing': False,
            'purchase_order_management': True,
            'monthly_report': False,
            'database_copy': False,
            'amount': 2000,
        }
    elif plan == 'm_e':
        plan_dict = {
            'stock_management_and_history': True,
            'smart_bulk_reel_addition': True,
            'reel_filtering': True,
            'reel_stocks_and_order_management': True,
            'products_management': True,
            'products_filtering': True,
            'production_line_handling': True,
            'daily_program_management': True,
            'daily_program_sharing': True,
            'purchase_order_management': True,
            'monthly_report': True,
            'database_copy': True,
            'amount': 4000,
        }
    elif plan == 'y_s':
        plan_dict = {
            'stock_management_and_history': False,
            'smart_bulk_reel_addition': False,
            'reel_filtering': False,
            'reel_stocks_and_order_management': False,
            'products_management': True,
            'products_filtering': False,
            'production_line_handling': True,
            'daily_program_management': True,
            'daily_program_sharing': False,
            'purchase_order_management': True,
            'monthly_report': False,
            'database_copy': False,
            'amount': 20000,
        }
    elif plan == 'y_e':
        plan_dict = {
            'stock_management_and_history': True,
            'smart_bulk_reel_addition': True,
            'reel_filtering': True,
            'reel_stocks_and_order_management': True,
            'products_management': True,
            'products_filtering': True,
            'production_line_handling': True,
            'daily_program_management': True,
            'daily_program_sharing': True,
            'purchase_order_management': True,
            'monthly_report': True,
            'database_copy': True,
            'amount': 40000,
        }
    return plan_dict


@login_required
def tenant_plans(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Tenant:register_tenant')
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        plan = plan_info_dict(plan_type)
        current_plan = TenantPlan.objects.filter(tenant=tenant, active=True).first()
        tenant_plan = TenantPlan.objects.create(
            tenant=tenant,
            name=plan_type,
            stock_management_and_history=plan['stock_management_and_history'],
            smart_bulk_reel_addition=plan['smart_bulk_reel_addition'],
            reel_filtering=plan['reel_filtering'],
            reels_stocks_and_order_management=plan['reel_stocks_and_order_management'],
            products_management=plan['products_management'],
            products_filtering=plan['products_filtering'],
            production_line_handling=plan['production_line_handling'],
            daily_program_management=plan['daily_program_management'],
            daily_program_sharing=plan['daily_program_sharing'],
            purchase_order_management=plan['purchase_order_management'],
            monthly_report=plan['monthly_report'],
            database_copy=plan['database_copy'],
            active=False,
            amount=plan['amount'],
        )
        if current_plan:
            tenant_plan.active_till = current_plan.active_till + timezone.timedelta(
                days=30 if plan_type.startswith('m_') else 365
            )
            tenant_plan.save()
            messages.success(request, 'Plan purchased successfully. It will be active after the current plan expires.')
        else:
            tenant_plan.active = True
            tenant_plan.active_till = timezone.now() + timezone.timedelta(
                days=30 if plan_type.startswith('m_') else 365
            )
            tenant_plan.save()
            messages.success(request, 'Plan purchased and activated successfully.')
        return redirect('Payments:plan_purchase_payment', plan_id=tenant_plan.id)
    tenant_plan = TenantPlan.objects.filter(tenant=tenant, active=True)
    next_tenant_plan = TenantPlan.objects.filter(tenant=tenant, active=False, active_till__gt=timezone.now()).exists()
    context = {
        'plan_type': tenant_plan.first().name if tenant_plan.exists() else None,
        'next_plan': next_tenant_plan,
    }
    return render(request, 'Tenant/tenant_plans.html', context)
