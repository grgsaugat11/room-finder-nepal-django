from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.listings.models import Listing
from .models import PhoneRevealLog, Advertisement


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]

    return request.META.get('REMOTE_ADDR')


@require_POST
def reveal_phone(request, listing_id):
    listing = get_object_or_404(
        Listing,
        id=listing_id,
        status=Listing.STATUS_APPROVED
    )

    session_key = f"revealed_phone_listing_{listing.id}"

    request.session[session_key] = True

    already_logged_key = f"phone_reveal_logged_{listing.id}"

    if not request.session.get(already_logged_key):
        PhoneRevealLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            listing=listing,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        request.session[already_logged_key] = True

    return JsonResponse({
        'success': True,
        'phone': listing.owner.phone
    })

def ad_click(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id, is_active=True)

    ad.clicks += 1
    ad.save(update_fields=['clicks'])

    if ad.link:
        return redirect(ad.link)

    return redirect('home')