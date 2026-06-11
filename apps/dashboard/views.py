from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from apps.listings.models import Listing, ListingDocument
from apps.reports.models import ListingReport
from django.core.paginator import Paginator
from apps.advertisements.models import Advertisement, PhoneRevealLog
from django.db import models

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first.")
            return redirect('login')

        if not request.user.is_platform_admin and not request.user.is_superuser:
            messages.error(request, "You are not allowed to access dashboard.")
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@admin_required
def dashboard_home(request):
    pending_count = Listing.objects.filter(status=Listing.STATUS_PENDING).count()
    approved_count = Listing.objects.filter(status=Listing.STATUS_APPROVED).count()
    rejected_count = Listing.objects.filter(status=Listing.STATUS_REJECTED).count()

    pending_reports_count = ListingReport.objects.filter(
        status=ListingReport.STATUS_PENDING
    ).count()

    recent_pending = Listing.objects.filter(
        status=Listing.STATUS_PENDING
    ).order_by('-created_at')[:5]
    
    active_ads_count = Advertisement.objects.filter(is_active=True).count()
    total_ad_impressions = Advertisement.objects.aggregate(
        total=models.Sum('impressions')
    )['total'] or 0
    total_ad_clicks = Advertisement.objects.aggregate(
        total=models.Sum('clicks')
    )['total'] or 0
    phone_reveals_count = PhoneRevealLog.objects.count()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_reports_count': pending_reports_count,
        'recent_pending': recent_pending,
        'active_ads_count': active_ads_count,
        'total_ad_impressions': total_ad_impressions,
        'total_ad_clicks': total_ad_clicks,
        'phone_reveals_count': phone_reveals_count,
    }

    return render(request, 'dashboard/home.html', context)

def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()

    if 'page' in query_params:
        query_params.pop('page')

    query_string = ''

    if query_params:
        query_string = '&' + query_params.urlencode()

    return page_obj, query_string

@login_required
@admin_required
def pending_listings(request):
    listings = Listing.objects.filter(
        status=Listing.STATUS_PENDING
    ).order_by('-created_at')

    page_obj, query_string = paginate_queryset(request, listings, per_page=10)

    return render(request, 'dashboard/pending_listings.html', {
        'listings': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
    })


@login_required
@admin_required
def approved_listings(request):
    listings = Listing.objects.filter(
        status=Listing.STATUS_APPROVED
    ).order_by('-approved_at', '-created_at')

    page_obj, query_string = paginate_queryset(request, listings, per_page=10)

    return render(request, 'dashboard/approved_listings.html', {
        'listings': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
    })


@login_required
@admin_required
def rejected_listings(request):
    listings = Listing.objects.filter(
        status=Listing.STATUS_REJECTED
    ).order_by('-updated_at')

    page_obj, query_string = paginate_queryset(request, listings, per_page=10)

    return render(request, 'dashboard/rejected_listings.html', {
        'listings': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
    })


@login_required
@admin_required
def review_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    return render(request, 'dashboard/review_listing.html', {
        'listing': listing
    })


@login_required
@admin_required
def approve_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    listing.status = Listing.STATUS_APPROVED
    listing.rejection_reason = ''
    listing.is_owner_verified = True
    listing.is_property_verified = True
    listing.approved_at = timezone.now()
    listing.save()

    if hasattr(listing, 'documents'):
        listing.documents.verification_status = ListingDocument.VERIFICATION_APPROVED
        listing.documents.reviewed_at = timezone.now()
        listing.documents.save()

    messages.success(request, "Listing approved successfully.")
    return redirect('pending_listings')


@login_required
@admin_required
def reject_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('rejection_reason')

        if not reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('review_listing', pk=listing.pk)

        listing.status = Listing.STATUS_REJECTED
        listing.rejection_reason = reason
        listing.is_owner_verified = False
        listing.is_property_verified = False
        listing.approved_at = None
        listing.save()

        if hasattr(listing, 'documents'):
            listing.documents.verification_status = ListingDocument.VERIFICATION_REJECTED
            listing.documents.admin_notes = reason
            listing.documents.reviewed_at = timezone.now()
            listing.documents.save()

        messages.success(request, "Listing rejected successfully.")
        return redirect('pending_listings')

    return redirect('review_listing', pk=listing.pk)

@login_required
@admin_required
def reports_queue(request):
    reports = ListingReport.objects.select_related(
        'listing',
        'reported_by',
        'listing__owner',
        'listing__district',
        'listing__province',
    ).order_by('-created_at')

    status = request.GET.get('status')

    if status:
        reports = reports.filter(status=status)

    page_obj, query_string = paginate_queryset(request, reports, per_page=10)

    context = {
        'reports': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'status_choices': ListingReport.STATUS_CHOICES,
        'selected_status': status,
    }

    return render(request, 'dashboard/reports_queue.html', context)


@login_required
@admin_required
def review_report(request, pk):
    report = get_object_or_404(
        ListingReport.objects.select_related(
            'listing',
            'reported_by',
            'listing__owner',
            'listing__district',
            'listing__province',
        ),
        pk=pk
    )

    return render(request, 'dashboard/review_report.html', {
        'report': report
    })


@login_required
@admin_required
def update_report_status(request, pk):
    report = get_object_or_404(ListingReport, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')

        valid_statuses = [
            ListingReport.STATUS_PENDING,
            ListingReport.STATUS_REVIEWED,
            ListingReport.STATUS_RESOLVED,
            ListingReport.STATUS_DISMISSED,
        ]

        if status not in valid_statuses:
            messages.error(request, "Invalid report status.")
            return redirect('review_report', pk=report.pk)

        report.status = status
        report.admin_notes = admin_notes
        report.reviewed_at = timezone.now()
        report.save()

        messages.success(request, "Report status updated successfully.")
        return redirect('reports_queue')

    return redirect('review_report', pk=report.pk)


@login_required
@admin_required
def remove_reported_listing(request, pk):
    report = get_object_or_404(ListingReport, pk=pk)
    listing = report.listing

    if request.method == 'POST':
        listing.status = Listing.STATUS_REJECTED
        listing.rejection_reason = "Listing removed after tenant report review."
        listing.is_owner_verified = False
        listing.is_property_verified = False
        listing.approved_at = None
        listing.save()

        report.status = ListingReport.STATUS_RESOLVED
        report.admin_notes = "Listing removed/rejected after report review."
        report.reviewed_at = timezone.now()
        report.save()

        messages.success(request, "Reported listing has been removed from public listings.")
        return redirect('reports_queue')

    return redirect('review_report', pk=report.pk)