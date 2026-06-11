from django.contrib import admin
from .models import Advertisement, PhoneRevealLog


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'position',
        'is_active',
        'start_date',
        'end_date',
        'impressions',
        'clicks',
        'created_at',
    )

    fields = (
        'title',
        'image',
        'video',
        'link',
        'position',
        'is_active',
        'start_date',
        'end_date',
    )

    list_filter = (
        'position',
        'is_active',
        'start_date',
        'end_date',
    )

    search_fields = (
        'title',
        'link',
    )

    readonly_fields = (
        'impressions',
        'clicks',
        'created_at',
    )


@admin.register(PhoneRevealLog)
class PhoneRevealLogAdmin(admin.ModelAdmin):
    list_display = (
        'listing',
        'user',
        'ip_address',
        'revealed_at',
    )

    search_fields = (
        'listing__title',
        'user__email',
        'ip_address',
    )

    list_filter = (
        'revealed_at',
    )

    readonly_fields = (
        'revealed_at',
    )