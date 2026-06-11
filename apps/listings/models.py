from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from apps.locations.models import Province, District


class Listing(models.Model):
    PROPERTY_SINGLE_ROOM = 'single_room'
    PROPERTY_TWO_ROOMS = 'two_rooms'
    PROPERTY_FLAT = 'flat'
    PROPERTY_APARTMENT = 'apartment'
    PROPERTY_HOUSE = 'house'
    PROPERTY_HOSTEL = 'hostel'
    PROPERTY_OFFICE = 'office'
    PROPERTY_SHUTTER = 'shutter'

    PROPERTY_TYPE_CHOICES = [
        (PROPERTY_SINGLE_ROOM, 'Single Room'),
        (PROPERTY_TWO_ROOMS, '2 Rooms'),
        (PROPERTY_FLAT, 'Flat'),
        (PROPERTY_APARTMENT, 'Apartment'),
        (PROPERTY_HOUSE, 'House'),
        (PROPERTY_HOSTEL, 'Hostel'),
        (PROPERTY_OFFICE, 'Office Space'),
        (PROPERTY_SHUTTER, 'Shutter'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    FURNISHED_FURNISHED = 'furnished'
    FURNISHED_UNFURNISHED = 'unfurnished'
    FURNISHED_SEMI = 'semi_furnished'

    FURNISHED_CHOICES = [
        (FURNISHED_FURNISHED, 'Furnished'),
        (FURNISHED_UNFURNISHED, 'Unfurnished'),
        (FURNISHED_SEMI, 'Semi-Furnished'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(
        max_length=30,
        choices=PROPERTY_TYPE_CHOICES
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name='listings'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='listings'
    )

    city = models.CharField(max_length=100)
    area = models.CharField(max_length=200)
    ward_number = models.PositiveIntegerField(null=True, blank=True)
    exact_address = models.CharField(max_length=255, blank=True)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    monthly_rent = models.PositiveIntegerField()
    security_deposit = models.PositiveIntegerField(default=0)

    bills_water_included = models.BooleanField(default=False)
    bills_electricity_included = models.BooleanField(default=False)
    bills_internet_included = models.BooleanField(default=False)

    furnished_status = models.CharField(
        max_length=30,
        choices=FURNISHED_CHOICES,
        default=FURNISHED_UNFURNISHED
    )

    available_date = models.DateField(null=True, blank=True)
    rules = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    rejection_reason = models.TextField(blank=True)

    is_owner_verified = models.BooleanField(default=False)
    is_property_verified = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.district and self.province:
            if self.district.province_id != self.province_id:
                raise ValidationError("Selected district does not belong to selected province.")

        if len(self.description.strip()) < 100:
            raise ValidationError("Description must be at least 100 characters long.")

    def __str__(self):
        return self.title

    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def short_description(self):
        if len(self.description) > 100:
            return self.description[:100] + "..."
        return self.description

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None

class ListingFacility(models.Model):
    listing = models.OneToOneField(
        Listing,
        on_delete=models.CASCADE,
        related_name='facilities'
    )

    car_parking = models.BooleanField(default=False)
    bike_parking = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    drinking_water = models.BooleanField(default=False)
    water_24_7 = models.BooleanField(default=False)
    attached_bathroom = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    cctv = models.BooleanField(default=False)
    security_guard = models.BooleanField(default=False)
    pet_allowed = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)

    def __str__(self):
        return f"Facilities for {self.listing.title}"
    
def listing_image_upload_path(instance, filename):
    return f"listings/{instance.listing.id}/images/{filename}"

class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to=listing_image_upload_path)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ListingImage.objects.filter(
                listing=self.listing,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.listing.title}"

def listing_document_upload_path(instance, filename):
    return f"listings/{instance.listing.id}/documents/{filename}"

class ListingDocument(models.Model):
    VERIFICATION_PENDING = 'pending'
    VERIFICATION_APPROVED = 'approved'
    VERIFICATION_REJECTED = 'rejected'

    VERIFICATION_CHOICES = [
        (VERIFICATION_PENDING, 'Pending'),
        (VERIFICATION_APPROVED, 'Approved'),
        (VERIFICATION_REJECTED, 'Rejected'),
    ]

    listing = models.OneToOneField(
        Listing,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    citizenship_front = models.ImageField(upload_to=listing_document_upload_path)
    citizenship_back = models.ImageField(upload_to=listing_document_upload_path)
    lalpurja = models.ImageField(upload_to=listing_document_upload_path)
    selfie_with_citizenship = models.ImageField(upload_to=listing_document_upload_path)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=VERIFICATION_PENDING
    )

    extracted_name = models.CharField(max_length=255, blank=True)
    extracted_citizenship_number = models.CharField(max_length=100, blank=True)
    extracted_address = models.CharField(max_length=255, blank=True)

    admin_notes = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Documents for {self.listing.title}"