import razorpay
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from Tenant.models import TenantPlan
from Tenant.views import get_tenant_for_user
from .models import PlanPurchase

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def plan_purchase_payment(request, plan_id):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Tenant:register_tenant')
    plan = TenantPlan.objects.get(id=plan_id)
    amount = plan.amount * 100
    currency = "INR"

    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='1'))
    razorpay_order_id = razorpay_order['id']

    # Create PlanPurchase record
    purchase = PlanPurchase.objects.create(
        tenant=tenant,
        status='PENDING',
        order_name=plan.name,
        order_amount=plan.amount,
        provider_order_id=razorpay_order_id,
        payment_id='',
        signature_id=''
    )

    context = {
        'callback_url': request.build_absolute_uri('/payment/plan_purchase_callback/'),
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_name': 'PlanPurchase',
        'description': 'Payment for Plan Purchase',
        'amount': amount,
        'purchase_id': purchase.id,
        'image': 'static/logo/small_logo.png'
    }
    return render(request, 'Payments/payment.html', context)


@csrf_exempt
def plan_purchase_callback(request):
    if request.method == 'POST':
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            purchase = PlanPurchase.objects.get(provider_order_id=razorpay_order_id)
            purchase.status = 'SUCCESS'
            purchase.payment_id = razorpay_payment_id
            purchase.signature_id = razorpay_signature
            purchase.save()
            tenant = purchase.tenant
            current_plan = TenantPlan.objects.filter(tenant=tenant, active=True, paid=True).first()
            if current_plan:
                # plan_id = request.POST.get('plan_id')
                new_plan = TenantPlan.objects.filter(tenant=tenant).latest('created_at')
                new_plan.active = False
                new_plan.active_till = current_plan.active_till + timezone.timedelta(
                    days=30 if new_plan.name.startswith('m_') else 365
                )
                new_plan.paid = True
                new_plan.save()
                messages.success(request, 'The new plan will be activated after the current plan expires.')
            else:
                # plan_id = request.POST.get('plan_id')
                new_plan = TenantPlan.objects.filter(tenant=tenant).latest('created_at')
                new_plan.active = True
                new_plan.active_till = timezone.now() + timezone.timedelta(
                    days=30 if new_plan.name.startswith('m_') else 365
                )
                new_plan.paid = True
                new_plan.save()
                messages.success(request, 'Payment successful. The new plan is now active.')
            return redirect('Corrugation:stocks')
        except razorpay.errors.SignatureVerificationError:
            purchase_id = request.POST.get('purchase_id')
            purchase = PlanPurchase.objects.get(id=purchase_id)
            purchase.status = 'FAILURE'
            purchase.save()
            plan_id = request.POST.get('plan_id')
            new_plan = TenantPlan.objects.get(id=plan_id)
            new_plan.delete()
            messages.error(request, 'Payment failed. Signature verification error.')
            return redirect('Tenant:tenant_plans')
    messages.error(request, 'Payment failed. Invalid request.')
    return redirect('Tenant:tenant_plans')
