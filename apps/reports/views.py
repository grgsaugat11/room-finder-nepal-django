from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.listings.models import Listing
from .forms import ListingReportForm
from .models import ListingReport


@login_required
def report_listing(request, listing_id):
    listing = get_object_or_404(
        Listing,
        id=listing_id,
        status=Listing.STATUS_APPROVED
    )

    existing_report = ListingReport.objects.filter(
        listing=listing,
        reported_by=request.user
    ).first()

    if existing_report:
        messages.warning(request, "You have already reported this listing.")
        return redirect('listing_detail', pk=listing.pk)

    if request.method == 'POST':
        form = ListingReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.listing = listing
            report.reported_by = request.user
            report.save()

            messages.success(request, "Report submitted. Admin will review it.")
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingReportForm()

    return render(request, 'reports/report_listing.html', {
        'form': form,
        'listing': listing,
    })