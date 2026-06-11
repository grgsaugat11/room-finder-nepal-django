from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Listing, ListingFacility, ListingImage, ListingDocument


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingFacilityInline(admin.StackedInline):
    model = ListingFacility
    extra = 0
    max_num = 1


class ListingDocumentInline(admin.StackedInline):
    model = ListingDocument
    extra = 0
    max_num = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'owner',
        'property_type',
        'province',
        'district',
        'monthly_rent',
        'status',
        'is_owner_verified',
        'is_property_verified',
        'created_at',
    )

    list_filter = (
        'status',
        'property_type',
        'province',
        'district',
        'is_owner_verified',
        'is_property_verified',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'owner__email',
        'owner__first_name',
        'owner__last_name',
        'city',
        'area',
    )

    readonly_fields = (
        'views_count',
        'created_at',
        'updated_at',
        'approved_at',
    )

    inlines = [
        ListingFacilityInline,
        ListingImageInline,
        ListingDocumentInline,
    ]


@admin.register(ListingFacility)
class ListingFacilityAdmin(admin.ModelAdmin):
    list_display = (
        'listing',
        'wifi',
        'car_parking',
        'bike_parking',
        'attached_bathroom',
        'pet_allowed',
    )


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = (
        'listing',
        'image',
        'is_primary',
        'uploaded_at',
    )


@admin.register(ListingDocument)
class ListingDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'listing',
        'verification_status',
        'uploaded_at',
        'reviewed_at',
    )

    list_filter = (
        'verification_status',
        'uploaded_at',
    )

    search_fields = (
        'listing__title',
        'listing__owner__email',
        'extracted_name',
        'extracted_citizenship_number',
    )