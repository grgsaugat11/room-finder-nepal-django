from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from apps.listings.models import Listing
from .models import Favorite
from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=9):
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
def toggle_favorite(request, listing_id):
    listing = get_object_or_404(
        Listing,
        id=listing_id,
        status=Listing.STATUS_APPROVED
    )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )

    if created:
        messages.success(request, "Listing added to favorites.")
    else:
        favorite.delete()
        messages.success(request, "Listing removed from favorites.")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('listing_detail', pk=listing.pk)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(
        user=request.user,
        listing__status=Listing.STATUS_APPROVED
    ).select_related('listing')

    page_obj, query_string = paginate_queryset(request, favorites, per_page=9)

    return render(request, 'favorites/my_favorites.html', {
        'favorites': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
    })