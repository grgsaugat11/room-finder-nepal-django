from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from apps.listings.models import Listing


class ListingReport(models.Model):
    REASON_FAKE = 'fake'
    REASON_WRONG_INFO = 'wrong_info'
    REASON_SCAM = 'scam'
    REASON_DUPLICATE = 'duplicate'
    REASON_OTHER = 'other'

    REASON_CHOICES = [
        (REASON_FAKE, 'Fake Listing'),
        (REASON_WRONG_INFO, 'Wrong Information'),
        (REASON_SCAM, 'Scam / Fraud'),
        (REASON_DUPLICATE, 'Duplicate Listing'),
        (REASON_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_RESOLVED = 'resolved'
    STATUS_DISMISSED = 'dismissed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reports'
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )

    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES
    )

    description = models.TextField(
        help_text="Explain why this listing seems suspicious."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('listing', 'reported_by')

    def __str__(self):
        return f"Report on {self.listing.title} by {self.reported_by.email}"