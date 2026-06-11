from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from apps.locations.models import Province, District
from .models import Listing, ListingImage, ListingDocument
from .forms import ListingForm, ListingFacilityForm, ListingDocumentForm, MultipleImageUploadForm
from django.core.paginator import Paginator
from apps.advertisements.models import Advertisement
from apps.advertisements.utils import get_active_ad

def home(request):
    listings = Listing.objects.filter(status=Listing.STATUS_APPROVED)

    query = request.GET.get('q')
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    property_type = request.GET.get('property_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    furnished_status = request.GET.get('furnished_status')
    sort = request.GET.get('sort')

    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query) |
            Q(area__icontains=query) |
            Q(district__name__icontains=query) |
            Q(province__name__icontains=query)
        )

    if province_id:
        listings = listings.filter(province_id=province_id)

    if district_id:
        listings = listings.filter(district_id=district_id)

    if property_type:
        listings = listings.filter(property_type=property_type)

    if min_price:
        listings = listings.filter(monthly_rent__gte=min_price)

    if max_price:
        listings = listings.filter(monthly_rent__lte=max_price)

    if furnished_status:
        listings = listings.filter(furnished_status=furnished_status)

    if sort == 'price_low':
        listings = listings.order_by('monthly_rent')
    elif sort == 'price_high':
        listings = listings.order_by('-monthly_rent')
    else:
        listings = listings.order_by('-created_at')

    provinces = Province.objects.all()

    page_obj, query_string = paginate_queryset(request, listings, per_page=9)
    
    home_top_ad = get_active_ad(Advertisement.POSITION_HOME_TOP)
    home_between_ad = get_active_ad(Advertisement.POSITION_HOME_BETWEEN_CARDS)

    context = {
        'listings': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'provinces': provinces,
        'property_types': Listing.PROPERTY_TYPE_CHOICES,
        'furnished_choices': Listing.FURNISHED_CHOICES,
        'selected_province': province_id,
        'selected_district': district_id,
        'home_top_ad': home_top_ad,
        'home_between_ad': home_between_ad,
    }

    return render(request, 'listings/home.html', context)

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

def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing,
        pk=pk,
        status=Listing.STATUS_APPROVED
    )

    listing.views_count += 1
    listing.save(update_fields=['views_count'])

    is_favorited = False

    if request.user.is_authenticated:
        is_favorited = listing.favorited_by.filter(
            user=request.user
        ).exists()

    phone_session_key = f"revealed_phone_listing_{listing.id}"
    phone_already_revealed = request.session.get(phone_session_key, False)
    
    detail_below_images_ad = get_active_ad(Advertisement.POSITION_DETAIL_BELOW_IMAGES)
    detail_sidebar_ad = get_active_ad(Advertisement.POSITION_DETAIL_SIDEBAR)
    phone_reveal_ad = get_active_ad(Advertisement.POSITION_PHONE_REVEAL_VIDEO)

    return render(request, 'listings/detail.html', {
        'listing': listing,
        'is_favorited': is_favorited,
        'phone_already_revealed': phone_already_revealed,
        'detail_below_images_ad': detail_below_images_ad,
        'detail_sidebar_ad': detail_sidebar_ad,
        'phone_reveal_ad': phone_reveal_ad,
    })

def load_districts(request):
    province_id = request.GET.get('province_id')
    districts = District.objects.filter(province_id=province_id).order_by('name')

    data = [
        {
            'id': district.id,
            'name': district.name
        }
        for district in districts
    ]

    return JsonResponse({'districts': data})

@login_required
def create_listing(request):
    if not request.user.is_landlord:
        messages.error(request, "Only landlords can post room listings.")
        return redirect('home')

    if not request.user.email_verified:
        messages.error(request, "Please verify your email before posting a listing.")
        return redirect('home')

    if request.method == 'POST':
        listing_form = ListingForm(request.POST)
        facility_form = ListingFacilityForm(request.POST)
        document_form = ListingDocumentForm(request.POST, request.FILES)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        if (
            listing_form.is_valid()
            and facility_form.is_valid()
            and document_form.is_valid()
            and image_form.is_valid()
        ):
            listing = listing_form.save(commit=False)
            listing.owner = request.user
            listing.status = Listing.STATUS_PENDING
            listing.save()

            facilities = facility_form.save(commit=False)
            facilities.listing = listing
            facilities.save()

            documents = document_form.save(commit=False)
            documents.listing = listing
            documents.save()

            images = request.FILES.getlist('images')

            for index, image in enumerate(images):
                ListingImage.objects.create(
                    listing=listing,
                    image=image,
                    is_primary=(index == 0)
                )

            messages.success(
                request,
                "Your listing has been submitted for admin review."
            )
            return redirect('my_listings')
    else:
        listing_form = ListingForm()
        facility_form = ListingFacilityForm()
        document_form = ListingDocumentForm()
        image_form = MultipleImageUploadForm()

    context = {
        'listing_form': listing_form,
        'facility_form': facility_form,
        'document_form': document_form,
        'image_form': image_form,
    }

    return render(request, 'listings/create_listing.html', context)

@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).order_by('-created_at')

    page_obj, query_string = paginate_queryset(request, listings, per_page=9)

    return render(request, 'listings/my_listings.html', {
        'listings': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
    })
    
@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(
        Listing,
        pk=pk,
        owner=request.user
    )

    if listing.status == Listing.STATUS_APPROVED:
        messages.error(
            request,
            "Approved listings cannot be edited directly. Please contact admin."
        )
        return redirect('my_listings')

    try:
        facilities = listing.facilities
    except Exception:
        facilities = None

    try:
        documents = listing.documents
    except Exception:
        documents = None

    if request.method == 'POST':
        listing_form = ListingForm(request.POST, instance=listing)
        facility_form = ListingFacilityForm(request.POST, instance=facilities)
        document_form = ListingDocumentForm(
            request.POST,
            request.FILES,
            instance=documents
        )

        if listing_form.is_valid() and facility_form.is_valid() and document_form.is_valid():
            listing = listing_form.save(commit=False)

            # If rejected listing is edited, send it back to admin review
            listing.status = Listing.STATUS_PENDING
            listing.rejection_reason = ''
            listing.is_owner_verified = False
            listing.is_property_verified = False
            listing.approved_at = None
            listing.save()

            facilities = facility_form.save(commit=False)
            facilities.listing = listing
            facilities.save()

            documents = document_form.save(commit=False)
            documents.listing = listing
            documents.verification_status = ListingDocument.VERIFICATION_PENDING
            documents.admin_notes = ''
            documents.reviewed_at = None
            documents.save()

            new_images = request.FILES.getlist('new_images')

            current_image_count = listing.images.count()
            total_image_count = current_image_count + len(new_images)

            if total_image_count > 15:
                messages.error(request, "You can have maximum 15 images per listing.")
                return redirect('edit_listing', pk=listing.pk)

            for image in new_images:
                ListingImage.objects.create(
                    listing=listing,
                    image=image,
                    is_primary=False
                )

            if not listing.images.filter(is_primary=True).exists():
                first_image = listing.images.first()
                if first_image:
                    first_image.is_primary = True
                    first_image.save()

            messages.success(
                request,
                "Listing updated and submitted for admin review again."
            )
            return redirect('my_listings')
    else:
        listing_form = ListingForm(instance=listing)
        facility_form = ListingFacilityForm(instance=facilities)
        document_form = ListingDocumentForm(instance=documents)

    return render(request, 'listings/edit_listing.html', {
        'listing': listing,
        'listing_form': listing_form,
        'facility_form': facility_form,
        'document_form': document_form,
    })


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(
        Listing,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        listing.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect('my_listings')

    return render(request, 'listings/delete_listing.html', {
        'listing': listing
    })


@login_required
def delete_listing_image(request, pk):
    image = get_object_or_404(
        ListingImage,
        pk=pk,
        listing__owner=request.user
    )

    listing = image.listing

    if listing.status == Listing.STATUS_APPROVED:
        messages.error(
            request,
            "Images of approved listings cannot be changed directly."
        )
        return redirect('my_listings')

    if request.method == 'POST':
        was_primary = image.is_primary
        image.delete()

        if was_primary:
            first_image = listing.images.first()
            if first_image:
                first_image.is_primary = True
                first_image.save()

        messages.success(request, "Image deleted successfully.")
        return redirect('edit_listing', pk=listing.pk)

    return redirect('edit_listing', pk=listing.pk)


@login_required
def set_primary_image(request, pk):
    image = get_object_or_404(
        ListingImage,
        pk=pk,
        listing__owner=request.user
    )

    listing = image.listing

    if listing.status == Listing.STATUS_APPROVED:
        messages.error(
            request,
            "Images of approved listings cannot be changed directly."
        )
        return redirect('my_listings')

    ListingImage.objects.filter(listing=listing).update(is_primary=False)

    image.is_primary = True
    image.save()

    messages.success(request, "Primary image updated successfully.")
    return redirect('edit_listing', pk=listing.pk)

@login_required
def landlord_dashboard(request):
    if not request.user.is_landlord:
        messages.error(request, "Only landlords can access this dashboard.")
        return redirect('home')

    listings = Listing.objects.filter(owner=request.user)

    total_listings = listings.count()
    pending_listings_count = listings.filter(status=Listing.STATUS_PENDING).count()
    approved_listings_count = listings.filter(status=Listing.STATUS_APPROVED).count()
    rejected_listings_count = listings.filter(status=Listing.STATUS_REJECTED).count()

    total_views = sum(listings.values_list('views_count', flat=True))

    recent_listings = listings.order_by('-created_at')[:5]

    most_viewed_listing = listings.order_by('-views_count').first()

    context = {
        'total_listings': total_listings,
        'pending_listings_count': pending_listings_count,
        'approved_listings_count': approved_listings_count,
        'rejected_listings_count': rejected_listings_count,
        'total_views': total_views,
        'recent_listings': recent_listings,
        'most_viewed_listing': most_viewed_listing,
    }

    return render(request, 'listings/landlord_dashboard.html', context)