from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import PaperReels
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


@login_required
def search_reels(request):
    query = request.GET.get('q', '')
    if query:
        results = PaperReels.objects.filter(
            Q(reel_number__icontains=query) |
            Q(bf__icontains=query) |
            Q(gsm__icontains=query) |
            Q(size__icontains=query) |
            Q(weight__icontains=query),
            used=False,
            tenant__owner__username=request.user.username,
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
                weight=weight
            )
            messages.success(request, 'Paper reel added successfully.')
            return redirect('Corrugation:paper_reels')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input. Please enter valid values.')
            return render(request, 'paper_reel.html')
    reels_list = PaperReels.objects.all()
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
        'used_reels': PaperReels.objects.filter(used=True).count(),
        'unused_reels': PaperReels.objects.filter(used=False).count(),
    }
    return render(request, 'paper_reel.html', context)


@login_required
def update_reel(request, pk):
    reel = get_object_or_404(PaperReels, pk=pk)
    if request.method == 'POST':
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
    reel = get_object_or_404(PaperReels, pk=pk)
    if request.method == 'POST':
        reel.used = True
        reel.save()
        messages.error(request, 'Paper reel deleted successfully.')
        return redirect('Corrugation:paper_reels')
    return redirect('Corrugation:paper_reels')


@login_required
def restore_reel(request, pk):
    reel = get_object_or_404(PaperReels, pk=pk)
    if request.method == 'POST':
        reel.used = False
        reel.save()
        messages.success(request, 'Paper reel restored successfully.')
        return redirect('Corrugation:paper_reels')
    return redirect('Corrugation:paper_reels')
