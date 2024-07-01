from django.shortcuts import render, redirect
from .models import Challan, ChallanItem
from django.contrib import messages
from Corrugation.views import get_tenant_for_user
from Corrugation.models import PurchaseOrder, TenantAddress, Tenant


def challans(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
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


def add_challan(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
# bundles of first product are being saved and rest are not being saved
    if request.method == 'POST':
        challan = Challan(
            tenant=tenant,
            order_no=request.POST.get('order_no'),
            order_date=request.POST.get('order_date'),
            challan_no=request.POST.get('challan_no'),
            challan_date=request.POST.get('challan_date'),
            billing_to=request.POST.get('billing_to'),
            shipping_to=request.POST.get('shipping_to'),
            vehicle_no=request.POST.get('vehicle_no'),
            challan_note=request.POST.get('challan_note')
        )
        challan.save()

        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        remarks = request.POST.getlist('remarks[]')
        bundle_sizes = request.POST.getlist('bundle_size[]')
        bundle_quantities = request.POST.getlist('bundle_quantity[]')

        bundle_index = 0

        for i in range(len(products)):
            challan_item = ChallanItem(
                challan=challan,
                challan_po=PurchaseOrder.objects.get(po_number=products[i]),
                quantity=quantities[i],
                remarks=remarks[i]
            )

            bundles = []
            while bundle_index < len(bundle_sizes) and bundle_sizes[bundle_index]:
                bundles.append({
                    'size': bundle_sizes[bundle_index],
                    'quantity': bundle_quantities[bundle_index]
                })
                bundle_index += 1
                if bundle_index % 3 == 0:
                    break

            challan_item.bundles = bundles
            challan_item.save()

        messages.success(request, 'Challan added successfully')
        return redirect('Billing:challans')

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
