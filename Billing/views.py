from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Challan, ChallanItem
from django.contrib import messages
from Corrugation.views import get_tenant_for_user
from Corrugation.models import PurchaseOrder, Tenant
from Tenant.models import TenantAddress


@login_required
def challans(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Tenant:register_tenant')
    tenant_challans = Challan.objects.filter(tenant=tenant)
    challan_items = ChallanItem.objects.filter(challan__in=tenant_challans)
    tenant_details = Tenant.objects.get(name=tenant.name)
    tenant_address = TenantAddress.objects.get(tenant__name=tenant.name)
    for challan in tenant_challans:
        challan.challan_items = challan_items.filter(challan=challan)
    context = {
        'tenant_details': tenant_details,
        'tenant_address': tenant_address,
        'challans': tenant_challans,
    }
    return render(request, 'Billing/challans.html', context)


@login_required
def add_challan(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Tenant:register_tenant')

    if request.method == "POST":
        print(request.POST)
        challan_no = request.POST.get('challan_no')
        challan_date = request.POST.get('challan_date')
        order_no = request.POST.get('order_no')
        order_date = request.POST.get('order_date')
        vehicle_no = request.POST.get('vehicle_no')
        billing_to = request.POST.get('billing_to')
        shipping_to = request.POST.get('shipping_to')
        challan_note = request.POST.get('challan_note')

        challan = Challan.objects.create(
            tenant=tenant,
            challan_no=challan_no,
            challan_date=challan_date,
            order_no=order_no,
            order_date=order_date,
            vehicle_no=vehicle_no,
            billing_to=billing_to,
            shipping_to=shipping_to,
            challan_note=challan_note
        )

        product_ids = request.POST.getlist('product[]')
        bundle_sizes = request.POST.getlist('bundle_size[]')
        bundle_quantities = request.POST.getlist('bundle_quantity[]')
        quantities = request.POST.getlist('quantity[]')
        remarks = request.POST.getlist('remarks[]')

        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = quantities[i]
            remark = remarks[i]
            bundles = []

            for j in range(len(bundle_sizes)):
                if j % len(product_ids) == i:
                    bundle_size = bundle_sizes[j]
                    bundle_quantity = bundle_quantities[j]
                    bundles.append({'size': bundle_size, 'quantity': bundle_quantity})
            po = PurchaseOrder.objects.get(po_number=product_id)
            ChallanItem.objects.create(
                challan=challan,
                challan_po=po,
                total_quantity=quantity,
                remarks=remark,
                bundles=bundles
            )

        messages.success(request, "Challan created successfully!")
        return redirect('Billing:add_challan')

    tenant_details = Tenant.objects.get(name=tenant.name)
    tenant_address = TenantAddress.objects.get(tenant__name=tenant.name)
    purchase_orders = PurchaseOrder.objects.filter(product_name__tenant=tenant).values(
        'id', 'po_number', 'product_name__product_name'
    )

    context = {
        'tenant_details': tenant_details,
        'tenant_address': tenant_address,
        'purchase_orders': purchase_orders
    }
    return render(request, 'Billing/add_challan.html', context=context)
