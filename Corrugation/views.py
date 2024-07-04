from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .models import (Tenant, TenantEmployees, PaperReels, Product, Partition,
                     PurchaseOrder, Dispatch, Stock, Program, Production,
                     ProductionReels, TenantBuyers)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import django.db.utils
import pandas as pd


def offline(request):
    return render(request, 'offline.html')


@login_required
def register_tenant(request):
    if request.method == 'POST':
        tenant_name = request.POST.get('tenant_name')
        tenant_logo = request.FILES.get('tenant_logo')
        user = request.user
        if Tenant.objects.filter(owner=user).exists():
            messages.info(request, 'You already have a tenant registered.')
            return redirect('Corrugation:register_tenant')
        Tenant.objects.create(
            owner=user,
            name=tenant_name,
            tenant_logo=tenant_logo
        )
        # Send email
        subject = 'Tenant Registration MultiBox'
        html_message = render_to_string('Corrugation/tenant_registration_email.html', {'user': user})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = user.email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

        messages.success(request, 'Tenant registered successfully.')
        messages.info(request, 'An email has been sent to you for the registration details.')
        return redirect('Corrugation:register_tenant')
    return render(request, 'Corrugation/register_tenant.html')


def get_tenant_for_user(request):
    try:
        tenant = Tenant.objects.get(owner=request.user)
        if not tenant.active:
            return redirect('inactive_tenant_page')
        return tenant
    except Tenant.DoesNotExist:
        try:
            tenant_employee = TenantEmployees.objects.get(user=request.user)
            tenant = tenant_employee.tenant
            if not tenant.active:
                return redirect('inactive_tenant_page')
            return tenant
        except TenantEmployees.DoesNotExist:
            return None


@login_required
def inactive_tenant_page(request):
    return render(request, 'Corrugation/inactive_tenant.html')


@login_required
def contact_support(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        send_mail(
            f'Support Request from {name}',
            message,
            email,
            ['janmaybhatt1903@gmail.com'],
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('Corrugation:stocks')
    return render(request, 'contact_support.html')


@login_required
def stocks(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        stock_quantity = request.POST.get('stock_quantity')
        try:
            stock_quantity = int(stock_quantity)
            product = Product.objects.get(tenant=tenant, product_name=product_name)
            stock, created = Stock.objects.get_or_create(product=product)
            stock.stock_quantity = stock_quantity
            stock.save()
        except (ValueError, TypeError):
            pass
        messages.info(request, 'Stock updated successfully.')
        return redirect('Corrugation:stocks')
    context = {
        'products': Product.objects.filter(tenant=tenant).values('product_name'),
        'stocks': Stock.objects.filter(product__tenant=tenant).values('product__product_name', 'stock_quantity', 'pk'),
    }
    return render(request, 'Corrugation/stocks.html', context)


@login_required
def delete_stock(request, pk):
    stock = Stock.objects.get(pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.error(request, 'Stock item cleared successfully.')
        return redirect(reverse('Corrugation:stocks'))
    return render(request, 'Corrugation/stocks.html', {'stock': stock})


@login_required
def search_reels(request):
    query = request.GET.get('q', '')
    tenant = get_tenant_for_user(request)

    if tenant is None:
        return JsonResponse({'results': [], 'size_counts': {}})

    results_data = []
    size_counts = {}

    if query:
        results = PaperReels.objects.filter(
            Q(reel_number__icontains=query) |
            Q(bf__icontains=query) |
            Q(gsm__icontains=query) |
            Q(size__icontains=query) |
            Q(weight__icontains=query),
            used=False,
            tenant=tenant,
        )

        for reel in results:
            results_data.append({
                'reel_number': reel.reel_number,
                'bf': reel.bf,
                'gsm': reel.gsm,
                'size': reel.size,
                'weight': reel.weight,
            })

            if reel.size in size_counts:
                size_counts[reel.size] += 1
            else:
                size_counts[reel.size] = 1

    return JsonResponse({'results': results_data, 'size_counts': size_counts})


@login_required
def paper_reels(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        reel_number = request.POST.get('reel_number')
        bf = request.POST.get('bf')
        gsm = request.POST.get('gsm')
        size = request.POST.get('size')
        weight = request.POST.get('weight')
        supplier = request.POST.get('supplier')
        try:
            bf = int(bf)
            gsm = int(gsm)
            size = float(size)
            weight = int(weight)
            PaperReels.objects.create(
                reel_number=reel_number,
                bf=bf,
                gsm=gsm,
                size=size,
                weight=weight,
                tenant=tenant,
                supplier=supplier,
            )
            messages.success(request, 'Paper reel added successfully.')
            return redirect('Corrugation:paper_reels')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input. Please enter valid values.')
            return render(request, 'Corrugation/paper_reel.html')

    reels_list = PaperReels.objects.filter(tenant=tenant).order_by('-created_at')
    paginator = Paginator(reels_list, 50)
    page = request.GET.get('page')
    try:
        reels = paginator.page(page)
    except PageNotAnInteger:
        reels = paginator.page(1)
    except EmptyPage:
        reels = paginator.page(paginator.num_pages)

    context = {
        'reels': reels,
        'used_reels': PaperReels.objects.filter(used=True, tenant=tenant).count(),
        'unused_reels': PaperReels.objects.filter(used=False, tenant=tenant).count(),
    }
    return render(request, 'Corrugation/paper_reel.html', context)


@login_required
def upload_bulk_reels(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        if 'reel_file' in request.FILES:
            file = request.FILES['reel_file']
            try:
                df = pd.read_excel(file)
                expected_columns = ['Reel Number', 'BF', 'GSM', 'Size', 'Weight']
                if list(df.columns) != expected_columns:
                    return JsonResponse({'error': 'Invalid file format'}, status=400)

                success_count = 0
                error_count = 0
                errors = []
                supplier = request.POST.get('supplier')
                for index, row in df.iterrows():
                    try:
                        PaperReels.objects.create(
                            tenant=tenant,
                            reel_number=int(row['Reel Number']),
                            bf=row['BF'],
                            gsm=row['GSM'],
                            size=row['Size'],
                            weight=row['Weight'],
                            supplier=supplier,
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {index + 1}: {str(e)}")

                return JsonResponse({'success_count': success_count, 'error_count': error_count, 'errors': errors})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def update_reel(request, pk):
    if request.method == 'POST':
        reel = get_object_or_404(PaperReels, pk=pk)
        reel.reel_number = request.POST.get('reel_number')
        reel.bf = request.POST.get('bf')
        reel.gsm = request.POST.get('gsm')
        reel.size = request.POST.get('size')
        reel.weight = request.POST.get('weight')
        reel.save()
        messages.info(request, 'Paper reel updated successfully.')
        return redirect('Corrugation:paper_reels')
    return redirect('Corrugation:paper_reels')


@login_required
def delete_reel(request, pk):
    if request.method == 'POST':
        reel = get_object_or_404(PaperReels, pk=pk)
        reel.used = True
        reel.save()
        messages.error(request, 'Paper reel deleted successfully.')
        return redirect('Corrugation:paper_reels')
    return redirect('Corrugation:paper_reels')


@login_required
def restore_reel(request, pk):
    if request.method == 'POST':
        reel = get_object_or_404(PaperReels, pk=pk)
        reel.used = False
        reel.save()
        messages.success(request, 'Paper reel restored successfully.')
        return redirect('Corrugation:paper_reels')
    return redirect('Corrugation:paper_reels')


@login_required
def reels_stock(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    products = Product.objects.filter(tenant=tenant).values('product_name', 'size', 'gsm', 'bf', 'weight')
    for product in products:
        product['stock_quantity'] = Stock.objects.filter(product__product_name=product['product_name']).aggregate(
            Sum('stock_quantity'))['stock_quantity__sum'] or 0
    context = {
        'products': products,
    }
    return render(request, 'Corrugation/reels_stock.html', context)


@login_required
def add_product(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        box_no = request.POST.get('box_no')
        material_code = request.POST.get('material_code')
        size = request.POST.get('size')
        inner_length = request.POST.get('inner_length', None)
        inner_breadth = request.POST.get('inner_breadth', None)
        inner_depth = request.POST.get('inner_depth', None)
        outer_length = request.POST.get('outer_length', None)
        outer_breadth = request.POST.get('outer_breadth', None)
        outer_depth = request.POST.get('outer_depth', None)
        color = request.POST.get('color', '')
        weight = request.POST.get('weight', None)
        ply = request.POST.get('ply', None)
        gsm = request.POST.get('gsm', None)
        bf = request.POST.get('bf', None)
        cs = request.POST.get('cs', None)
        product = Product.objects.create(
            product_name=product_name,
            box_no=box_no,
            material_code=material_code,
            size=size,
            inner_length=inner_length,
            inner_breadth=inner_breadth,
            inner_depth=inner_depth,
            outer_length=outer_length,
            outer_breadth=outer_breadth,
            outer_depth=outer_depth,
            color=color,
            weight=weight,
            ply=ply,
            gsm=gsm,
            bf=bf,
            cs=cs,
            tenant=tenant
        )

        partition_data = zip(
            request.POST.getlist('partition_size'),
            request.POST.getlist('partition_od'),
            request.POST.getlist('deckle_cut'),
            request.POST.getlist('length_cut'),
            request.POST.getlist('partition_type'),
            request.POST.getlist('ply_no'),
            request.POST.getlist('partition_weight'),
            request.POST.getlist('partition_gsm'),
            request.POST.getlist('partition_bf')
        )

        for partition in partition_data:
            Partition.objects.create(
                product_name=product,
                partition_size=partition[0],
                partition_od=partition[1],
                deckle_cut=partition[2],
                length_cut=partition[3],
                partition_type=partition[4],
                ply_no=partition[5],
                partition_weight=partition[6],
                gsm=partition[7],
                bf=partition[8]
            )
        messages.success(request, 'Product added successfully.')
        return redirect('Corrugation:add_product')
    context = {
        'products': Product.objects.filter(archive=False, tenant=tenant).values('product_name', 'pk'),
    }
    return render(request, 'Corrugation/products.html', context)


@login_required
def product_archive(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    products = Product.objects.filter(archive=True, tenant=tenant).values('product_name', 'pk')
    context = {
        'products': products,
    }
    return render(request, 'Corrugation/products_archive.html', context)


@login_required
def update_products(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.product_name = request.POST.get('product_name')
        product.box_no = request.POST.get('box_no')
        product.material_code = request.POST.get('material_code')
        product.size = request.POST.get('size')
        product.inner_length = request.POST.get('inner_length', None)
        product.inner_breadth = request.POST.get('inner_breadth', None)
        product.inner_depth = request.POST.get('inner_depth', None)
        product.outer_length = request.POST.get('outer_length', None)
        product.outer_breadth = request.POST.get('outer_breadth', None)
        product.outer_depth = request.POST.get('outer_depth', None)
        product.color = request.POST.get('color', '')
        product.weight = request.POST.get('weight', None)
        product.ply = request.POST.get('ply', None)
        product.gsm = request.POST.get('gsm', None)
        product.bf = request.POST.get('bf', None)
        product.cs = request.POST.get('cs', None)
        product.save()

        # Collect existing partitions for the product
        existing_partitions = list(product.partition_set.all())
        partitions_data = {}

        # Iterate through POST data to organize it by partition
        for key, value in request.POST.items():
            if key.startswith('partitions['):
                # Extract the partition index and the field name
                part_idx = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]

                # Initialize the dictionary for this partition if not already
                if part_idx not in partitions_data:
                    partitions_data[part_idx] = {}

                # Assign the value to the appropriate field in the partition
                partitions_data[part_idx][field_name] = value

        # Now process each partition
        for idx, partition_data in partitions_data.items():
            if int(idx) <= len(existing_partitions):
                # Update existing partition
                partition = existing_partitions[int(idx) - 1]
            else:
                # Create new partition
                partition = Partition(product_name=product)

            partition.partition_type = partition_data.get('type')
            partition.partition_size = partition_data.get('size')
            partition.partition_od = partition_data.get('od')
            partition.deckle_cut = partition_data.get('deckle_cut')
            partition.length_cut = partition_data.get('length_cut')
            partition.ply_no = partition_data.get('ply_no')
            partition.partition_weight = partition_data.get('weight')
            partition.gsm = partition_data.get('gsm')
            partition.bf = partition_data.get('bf')
            partition.product_name = product
            partition.save()
        messages.info(request, 'Product updated successfully.')
        return redirect('Corrugation:products_detail', pk=pk)
    return redirect('Corrugation:add_product')


@login_required
def delete_products(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.archive = True
        product.save()
        messages.error(request, 'Product archived successfully.')
        return redirect('Corrugation:add_product')
    return redirect('Corrugation:add_product')


@login_required
def restore_products(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.archive = False
        product.save()
        messages.success(request, 'Product restored successfully.')
        return redirect('Corrugation:add_product')
    return redirect('Corrugation:add_product')


@login_required
def products_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, archive=False)
    partitions = Partition.objects.filter(product_name=product)
    context = {
        'product': product,
        'partitions': partitions
    }
    return render(request, 'Corrugation/product_detail.html', context)


@login_required
def product_detail_archive(request, pk):
    product = get_object_or_404(Product, pk=pk, archive=True)
    partitions = Partition.objects.filter(product_name=product)
    context = {
        'product': product,
        'partitions': partitions
    }
    return render(request, 'Corrugation/product_detail_archive.html', context)


@login_required
def purchase_order(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    po_active_count_by_given_by = (PurchaseOrder.objects.filter(active=True, product_name__tenant=tenant)
                                   .values_list('po_given_by', flat=True).distinct())

    context = {
        'purchase_order_list': po_active_count_by_given_by,
        'products': Product.objects.filter(tenant=tenant).values('product_name', 'pk'),
        'po_given_by_choices': TenantBuyers.objects.filter(tenant=tenant).values('buyer_name'),
    }
    return render(request, 'Corrugation/purchase_order.html', context)


@login_required
def purchase_order_archive(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    po_active_count_by_given_by = (PurchaseOrder.objects.filter(active=False, product_name__tenant=tenant)
                                   .values_list('po_given_by', flat=True).distinct())
    context = {
        'purchase_order_list': po_active_count_by_given_by,
    }
    return render(request, 'Corrugation/purchase_order_archive.html', context)


@login_required
def add_purchase_order_detailed(request):
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    if request.method == 'POST':
        product_id = request.POST['product_name']
        product = get_object_or_404(Product, id=product_id)
        po_given_by = request.POST['po_given_by']
        po_number = request.POST['po_number']
        po_date = request.POST['po_date']
        rate = request.POST['rate']
        po_quantity = request.POST['po_quantity']

        PurchaseOrder.objects.create(
            product_name=product,
            po_given_by=po_given_by,
            po_number=po_number,
            po_date=po_date,
            rate=rate,
            po_quantity=po_quantity
        )
        return redirect('Corrugation:purchase_order')


@login_required
def add_purchase_order_detail(request, po_given_by):
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    purchase_orders = PurchaseOrder.objects.filter(
        po_given_by=po_given_by,
        active=True
    ).select_related('product_name')

    # Get dispatches for the selected purchase orders
    purchase_order_ids = purchase_orders.values_list('pk', flat=True)
    dispatches = Dispatch.objects.filter(po_id__in=purchase_order_ids).select_related('po')
    # Group dispatches by purchase order
    dispatches_dict = {}
    for dispatch in dispatches:
        if dispatch.po_id not in dispatches_dict:
            dispatches_dict[dispatch.po_id] = []
        dispatches_dict[dispatch.po_id].append(dispatch)

    # Add dispatches to purchase orders
    for po in purchase_orders:
        po.dispatches = dispatches_dict.get(po.id, [])
    for po in purchase_orders:
        total_dispatch_quantity = sum(dispatch.dispatch_quantity for dispatch in po.dispatches)
        po.remaining_quantity = po.po_quantity - total_dispatch_quantity
        po.max_remaining_quantity = po.po_quantity + (po.po_quantity * 5 / 100) - total_dispatch_quantity
        po.material_code = po.product_name.material_code
        po.box_no = po.product_name.box_no

    context = {
        'purchase_orders': purchase_orders,
    }
    return render(request, 'Corrugation/purchase_order_details.html', context)


@login_required
def purchase_order_detail_archive(request, po_given_by):
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    purchase_orders = PurchaseOrder.objects.filter(
        po_given_by=po_given_by,
        active=False
    ).select_related('product_name')

    # Get dispatches for the selected purchase orders
    purchase_order_ids = purchase_orders.values_list('pk', flat=True)
    dispatches = Dispatch.objects.filter(po_id__in=purchase_order_ids).select_related('po')
    # Group dispatches by purchase order
    dispatches_dict = {}
    for dispatch in dispatches:
        if dispatch.po_id not in dispatches_dict:
            dispatches_dict[dispatch.po_id] = []
        dispatches_dict[dispatch.po_id].append(dispatch)

    # Add dispatches to purchase orders
    for po in purchase_orders:
        po.dispatches = dispatches_dict.get(po.id, [])
    for po in purchase_orders:
        total_dispatch_quantity = sum(dispatch.dispatch_quantity for dispatch in po.dispatches)
        po.remaining_quantity = po.po_quantity - total_dispatch_quantity
        po.max_remaining_quantity = po.po_quantity + (po.po_quantity * 5 / 100) - total_dispatch_quantity
        po.material_code = po.product_name.material_code
        po.box_no = po.product_name.box_no
    context = {
        'purchase_orders': purchase_orders,
    }
    return render(request, 'Corrugation/purchase_order_details_archive.html', context)


@login_required
def delete_purchase_order(request, pk):
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    if request.method == 'POST':
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.active = False
        po.save()
        messages.error(request, 'Purchase order deleted successfully.')
        return redirect('Corrugation:purchase_order')


@login_required
def restore_purchase_order(request, pk):
    if not request.user.is_staff:
        return redirect('Corrugation:contact_support')
    if request.method == 'POST':
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.active = True
        po.save()
        messages.success(request, 'Purchase order Restored successfully.')
        return redirect('Corrugation:purchase_order')


@login_required
def add_dispatch(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        po = get_object_or_404(PurchaseOrder, id=pk)
        dispatch_date = request.POST['dispatch_date']
        dispatch_quantity = request.POST['dispatch_quantity']

        Dispatch.objects.create(
            po=po,
            dispatch_date=dispatch_date,
            dispatch_quantity=dispatch_quantity
        )
        try:
            stock, created = Stock.objects.get_or_create(product=po.product_name)
            stock.stock_quantity -= int(dispatch_quantity)
            stock.save()
        except django.db.utils.IntegrityError:
            pass
        messages.success(request, 'Dispatch added successfully.')
        return redirect('Corrugation:add_purchase_order_detail', po_given_by=po.po_given_by)
    return redirect('Corrugation:purchase_order')


@login_required
def daily_program(request):
    if request.method == 'POST':
        # Extract data from POST request
        data = request.POST
        product_name = data.get('product_name')
        program_quantity = data.get('program_quantity')
        program_date_str = data.get('program_date')
        program_notes = data.get('program_notes')
        # Convert program_date from string to datetime
        program_date = datetime.strptime(program_date_str, '%Y-%m-%d').date()
        # Create a new Program instance
        Program.objects.create(
            product=Product.objects.get(product_name=product_name),
            program_quantity=program_quantity,
            program_date=program_date,
            program_notes=program_notes
        )
        messages.success(request, 'Program added successfully.')
        return redirect('Corrugation:daily_program')
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    programs = Program.objects.filter(active=True, product__tenant=tenant).order_by('-program_date')
    # Prepare data to return
    programs_data = []
    for program in programs:
        # Get related product
        product = program.product

        # Get related partitions for the product
        partitions = Partition.objects.filter(product_name=product)

        # Prepare partition data
        partitions_data = []
        for partition in partitions:
            partition_data = {
                'partition_size': partition.partition_size,
                'partition_od': partition.partition_od,
                'deckle_cut': partition.deckle_cut,
                'length_cut': partition.length_cut,
                'partition_type': partition.get_partition_type_display(),
                'ply_no': partition.get_ply_no_display(),
                'partition_weight': partition.partition_weight
            }
            partitions_data.append(partition_data)

        # Prepare program data
        program_data = {
            'product_name': product.product_name,
            'box_no': product.box_no,
            'material_code': product.material_code,
            'size': product.size,
            'inner_length': product.inner_length,
            'inner_breadth': product.inner_breadth,
            'inner_depth': product.inner_depth,
            'outer_length': product.outer_length,
            'outer_breadth': product.outer_breadth,
            'outer_depth': product.outer_depth,
            'gsm': product.gsm,
            'bf': product.bf,
            'color': product.color,
            'weight': product.weight,
            'partitions': partitions_data,
            'program_quantity': program.program_quantity,
            'program_date': program.program_date.strftime('%Y-%m-%d'),
            'program_notes': program.program_notes,
        }
        programs_data.append(program_data)
    context = {
        'programs': programs_data,
        'products': Product.objects.filter(tenant=tenant).values('product_name'),
    }
    return render(request, 'Corrugation/program.html', context)


@login_required
def program_archive(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    programs = Program.objects.filter(active=False, product__tenant=tenant).order_by('-program_date')
    programs_data = []
    for program in programs:
        product = program.product
        partitions = Partition.objects.filter(product_name=product)
        partitions_data = []
        for partition in partitions:
            partition_data = {
                'partition_size': partition.partition_size,
                'partition_od': partition.partition_od,
                'deckle_cut': partition.deckle_cut,
                'length_cut': partition.length_cut,
                'partition_type': partition.get_partition_type_display(),
                'ply_no': partition.get_ply_no_display(),
                'partition_weight': partition.partition_weight
            }
            partitions_data.append(partition_data)
        program_data = {
            'product_name': product.product_name,
            'box_no': product.box_no,
            'material_code': product.material_code,
            'size': product.size,
            'inner_length': product.inner_length,
            'inner_breadth': product.inner_breadth,
            'inner_depth': product.inner_depth,
            'outer_length': product.outer_length,
            'outer_breadth': product.outer_breadth,
            'outer_depth': product.outer_depth,
            'gsm': product.gsm,
            'bf': product.bf,
            'color': product.color,
            'weight': product.weight,
            'partitions': partitions_data,
            'program_quantity': program.program_quantity,
            'program_date': program.program_date.strftime('%Y-%m-%d'),
            'program_notes': program.program_notes,
        }
        programs_data.append(program_data)
    context = {
        'programs': programs_data,
    }
    return render(request, 'Corrugation/program_archive.html', context)


@login_required
def edit_program_view(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        program_quantity = request.POST.get('program_quantity')
        program_date = request.POST.get('program_date')
        program_notes = request.POST.get('program_notes')
        program = get_object_or_404(Program, product__product_name=product_name)
        program.product_name = product_name
        program.program_quantity = program_quantity
        program.program_date = program_date
        program.program_notes = program_notes
        program.save()
        messages.info(request, 'Program updated successfully.')
        return redirect(reverse('Corrugation:daily_program'))
    return redirect(reverse('Corrugation:daily_program'))


@login_required
def delete_program_view(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        program = Program.objects.get(product__product_name=product_name)
        program.active = False
        program.save()
        messages.error(request, 'Program deleted successfully.')
        return redirect(reverse('Corrugation:daily_program'))
    return redirect(reverse('Corrugation:daily_program'))


@login_required
def production(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        # Extract data from POST request
        data = request.POST
        product_name = data.get('product')
        reel_numbers = data.getlist('reels')  # getlist to handle multiple reels
        production_quantity = data.get('production_quantity')

        # Create a new Production instance
        product_instance = Product.objects.filter(product_name=product_name, tenant=tenant)
        production_object = Production.objects.create(
            product=product_instance,
            production_quantity=production_quantity,
            production_date=timezone.now(),
        )
        stock, create = Stock.objects.get_or_create(product=product_instance)
        stock.stock_quantity += int(production_quantity)
        stock.save()
        # Create new ProductionReels instances for each reel number
        for reel_number in reel_numbers:
            reel_instance = PaperReels.objects.get(reel_number=reel_number, tenant=tenant)
            ProductionReels.objects.create(
                production=production_object,
                reel=reel_instance,
            )
        messages.success(request, 'Production added successfully.')
        return redirect('Corrugation:production')

    production_objects = Production.objects.filter(active=True)
    production_data = []
    for production_object in production_objects:
        production_reels = ProductionReels.objects.filter(production=production_object)
        reels_data = [(reel.reel.reel_number, reel.reel.size, reel.reel.weight) for reel in production_reels]
        production_data.append({
            'pk': production_object.pk,
            'product_name': production_object.product.product_name,
            'production_quantity': production_object.production_quantity,
            'production_date': production_object.production_date,
            'reels': reels_data,
        })

    context = {
        'products': Product.objects.filter(tenant=tenant).values('product_name'),
        'reels': PaperReels.objects.filter(tenant=tenant).values('reel_number', 'size', 'weight').order_by('size'),
        'productions': production_data,
    }
    return render(request, 'Corrugation/production.html', context)


@login_required
def production_archive(request):
    tenant = get_tenant_for_user(request)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    production_objects = Production.objects.filter(active=False, product__tenant=tenant)
    production_data = []
    for production_object in production_objects:
        production_reels = ProductionReels.objects.filter(production=production_object)
        reels_data = [reel.reel.reel_number for reel in production_reels]
        production_data.append({
            'pk': production_object.pk,
            'product_name': production_object.product.product_name,
            'production_quantity': production_object.production_quantity,
            'production_date': production_object.production_date,
            'reels': reels_data,
        })

    context = {
        'productions': production_data,
    }
    return render(request, 'Corrugation/production_archive.html', context)


@login_required
def update_production_quantity(request):
    if request.method == 'POST':
        production_object = get_object_or_404(Production, pk=request.POST.get('pk'))
        production_object.production_quantity = request.POST.get('production_quantity')
        production_object.save()
        messages.info(request, 'Production quantity updated successfully.')
        return redirect('Corrugation:production')
    return redirect('Corrugation:production')


@login_required
def add_reel_to_production(request):
    if request.method == 'POST':
        production_object = get_object_or_404(Production, pk=request.POST.get('pk'))
        reel_number = request.POST.get('reel_number')
        try:
            reel = PaperReels.objects.get(reel_number=reel_number)
            ProductionReels.objects.create(production=production_object, reel=reel)
        except PaperReels.DoesNotExist:
            # Optionally handle the error if reel does not exist
            pass
        messages.success(request, 'Reel added to production successfully.')
        return redirect('Corrugation:production')
    return redirect('Corrugation:production')


@login_required
def delete_production(request):
    if request.method == 'POST':
        production_object = get_object_or_404(Production, pk=request.POST.get('pk'))
        # delete reels that are used in production
        used_reels = ProductionReels.objects.filter(production=production_object)
        for reel in used_reels:
            PaperReels.objects.filter(reel_number=reel.reel.reel_number).used = True
        # ProductionReels.objects.filter(production=production_object).delete()
        production_object.active = False
        production_object.save()
        messages.error(request, 'Production deleted successfully.')
        return redirect('Corrugation:production')
    return redirect('Corrugation:production')
