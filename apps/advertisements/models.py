from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.listings.models import Listing


class Advertisement(models.Model):
    POSITION_HOME_TOP = 'home_top'
    POSITION_HOME_BETWEEN_CARDS = 'home_between_cards'
    POSITION_DETAIL_BELOW_IMAGES = 'detail_below_images'
    POSITION_DETAIL_SIDEBAR = 'detail_sidebar'
    POSITION_PHONE_REVEAL_VIDEO = 'phone_reveal_video'

    POSITION_CHOICES = [
        (POSITION_HOME_TOP, 'Homepage Top Banner'),
        (POSITION_HOME_BETWEEN_CARDS, 'Homepage Between Cards'),
        (POSITION_DETAIL_BELOW_IMAGES, 'Listing Detail Below Images'),
        (POSITION_DETAIL_SIDEBAR, 'Listing Detail Sidebar'),
        (POSITION_PHONE_REVEAL_VIDEO, 'Phone Reveal Video Ad'),
    ]

    title = models.CharField(max_length=150)

    image = models.ImageField(
        upload_to='advertisements/',
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to='advertisements/videos/',
        blank=True,
        null=True
    )

    link = models.URLField(blank=True)

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES
    )

    is_active = models.BooleanField(default=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_currently_active(self):
        today = timezone.now().date()

        if not self.is_active:
            return False

        if self.start_date and self.start_date > today:
            return False

        if self.end_date and self.end_date < today:
            return False

        return True

    def __str__(self):
        return f"{self.title} - {self.get_position_display()}"


class PhoneRevealLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_reveals',
        null=True,
        blank=True
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='phone_reveal_logs'
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    revealed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-revealed_at']

    def __str__(self):
        if self.user:
            return f"{self.user.email} revealed phone for {self.listing.title}"
        return f"Anonymous reveal for {self.listing.title}"