from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, TenantEmployees, PaperReels, Product, Partition
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
        messages.success(request, 'Tenant registered successfully.')
        return redirect('Corrugation:register_tenant')
    return render(request, 'register_tenant.html')


def get_tenant_for_user(user):
    try:
        return Tenant.objects.get(owner=user)
    except Tenant.DoesNotExist:
        try:
            tenant_employee = TenantEmployees.objects.get(user=user)
            return tenant_employee.tenant
        except TenantEmployees.DoesNotExist:
            return None


@login_required
def search_reels(request):
    query = request.GET.get('q', '')
    tenant = get_tenant_for_user(request.user)

    if tenant is None:
        return JsonResponse({'results': []})

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
        results_data = [
            {
                'reel_number': reel.reel_number,
                'bf': reel.bf,
                'gsm': reel.gsm,
                'size': reel.size,
                'weight': reel.weight,
            }
            for reel in results
        ]
    else:
        results_data = []

    return JsonResponse({'results': results_data})


@login_required
def paper_reels(request):
    tenant = get_tenant_for_user(request.user)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    if request.method == 'POST':
        reel_number = request.POST.get('reel_number')
        bf = request.POST.get('bf')
        gsm = request.POST.get('gsm')
        size = request.POST.get('size')
        weight = request.POST.get('weight')

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
            )
            messages.success(request, 'Paper reel added successfully.')
            return redirect('Corrugation:paper_reels')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input. Please enter valid values.')
            return render(request, 'paper_reel.html')

    reels_list = PaperReels.objects.filter(tenant=tenant)
    paginator = Paginator(reels_list, 20)  # Show 20 reels per page
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
    return render(request, 'paper_reel.html', context)


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
def add_product(request):
    tenant = get_tenant_for_user(request.user)
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
    return render(request, 'products.html', context)


@login_required
def product_archive(request):
    tenant = get_tenant_for_user(request.user)
    if tenant is None:
        messages.error(request, 'You are not associated with any tenant.')
        return redirect('Corrugation:register_tenant')
    products = Product.objects.filter(archive=True, tenant=tenant).values('product_name', 'pk')
    context = {
        'products': products,
    }
    return render(request, 'products_archive.html', context)


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
        for partition_data in partitions_data.values():
            # Retrieve or create a new Partition instance
            partition = get_object_or_404(Partition, product_name=product)
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
    return render(request, 'product_detail.html', context)


@login_required
def product_detail_archive(request, pk):
    product = get_object_or_404(Product, pk=pk, archive=True)
    partitions = Partition.objects.filter(product_name=product)
    context = {
        'product': product,
        'partitions': partitions
    }
    return render(request, 'product_detail_archive.html', context)
