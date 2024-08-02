import razorpay
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
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
    amount = plan.price * 100
    currency = "INR"

    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='1'))
    razorpay_order_id = razorpay_order['id']

    # Create PlanPurchase record
    purchase = PlanPurchase.objects.create(
        tenant=tenant,
        status='PENDING',
        order_name=plan.name,
        order_amount=plan.price,
        provider_order_id=razorpay_order_id,
        payment_id='',
        signature_id=''
    )

    context = {
        'plan': plan,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'currency': currency,
        'purchase_id': purchase.id,
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
            purchase_id = request.POST.get('purchase_id')
            purchase = PlanPurchase.objects.get(id=purchase_id)
            purchase.status = 'SUCCESS'
            purchase.payment_id = razorpay_payment_id
            purchase.signature_id = razorpay_signature
            purchase.save()
            plan_id = request.POST.get('plan_id')
            plan = TenantPlan.objects.get(id=plan_id)
            plan.active = True
            plan.active_till = timezone.now() + timezone.timedelta(days=30)
            plan.save()
            messages.success(request, 'Payment Successful, Plan is Activated')
            return JsonResponse({'status': 'success'})
        except razorpay.errors.SignatureVerificationError:
            purchase_id = request.POST.get('purchase_id')
            purchase = PlanPurchase.objects.get(id=purchase_id)
            purchase.status = 'FAILURE'
            purchase.save()
            plan_id = request.POST.get('plan_id')
            plan = TenantPlan.objects.get(id=plan_id)
            plan.delete()
            messages.error(request, 'Payment Failed, Signature Verification Error')
            return JsonResponse({'status': 'failure'})
    messages.error(request, 'Payment Failed, Invalid Request')
    return JsonResponse({'status': 'failure'})
