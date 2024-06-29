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
    context = {
        'challans': tenant_challans,
        'challan_items': challan_items
    }
    return render(request, 'Billing/challans.html', context)


def add_challan(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        challan = Challan()
        challan.tenant = tenant
        challan.order_no = request.POST.get('order_no')
        challan.order_date = request.POST.get('order_date')
        challan.challan_no = request.POST.get('challan_no')
        challan.challan_date = request.POST.get('challan_date')
        challan.buyer_name = request.POST.get('buyer_name')
        challan.vehicle_no = request.POST.get('vehicle_no')
        challan.challan_note = request.POST.get('challan_note')
        challan.save()
        for item in request.POST.get('items'):
            challan_item = ChallanItem()
            challan_item.challan = challan
            challan_item.challan_po = item.get('challan_po')
            challan_item.bundles = item.get('bundles')
            challan_item.quantity = item.get('quantity')
            challan_item.remarks = item.get('remarks')
            challan_item.save()
        messages.success(request, 'Challan added successfully')
        return redirect('Billing:challans')
    tenant_logo = Tenant.objects.get(name=tenant).logo
    tenant_address = TenantAddress.objects.get(tenant=tenant)
    purchase_orders = PurchaseOrder.objects.filter(tenant=tenant).values(
        'id', 'po_number', 'product_name__product_name'
    )
    context = {
        'tenant_logo': tenant_logo,
        'tenant_address': tenant_address,
        'purchase_orders': purchase_orders
    }
    return render(request, 'Billing/add_challan.html', context=context)
