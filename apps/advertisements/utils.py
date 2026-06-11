from django.db.models import Q, F
from django.utils import timezone

from .models import Advertisement


def get_active_ad(position, increase_impression=True):
    today = timezone.now().date()

    ad = Advertisement.objects.filter(
        position=position,
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today),
        Q(end_date__isnull=True) | Q(end_date__gte=today),
    ).first()

    if ad and increase_impression:
        Advertisement.objects.filter(id=ad.id).update(
            impressions=F('impressions') + 1
        )

        ad.refresh_from_db(fields=['impressions'])

    return ad