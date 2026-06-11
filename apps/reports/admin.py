from django.contrib import admin
from .models import ListingReport


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = (
        'listing',
        'reported_by',
        'reason',
        'status',
        'created_at',
    )

    list_filter = (
        'reason',
        'status',
        'created_at',
    )

    search_fields = (
        'listing__title',
        'reported_by__email',
        'description',
    )

    readonly_fields = (
        'created_at',
        'reviewed_at',
    )