from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from apps.accounts.models import User
from apps.locations.models import District, Province
from .forms import ListingForm, ListingImageEditForm
from .models import Listing, ListingDocument, ListingImage


def uploaded_photo():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'green').save(buffer, format='JPEG')
    return SimpleUploadedFile('room.jpg', buffer.getvalue(), content_type='image/jpeg')


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ListingRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email='owner@example.com', phone='9800000000', role='landlord', email_verified=True
        )
        cls.province = Province.objects.create(name='Bagmati')
        cls.district = District.objects.create(name='Kathmandu', province=cls.province)
        cls.listing = Listing.objects.create(
            owner=cls.owner, title='Sunny flat', description='A bright, welcoming rental home. ' * 5,
            property_type='flat', province=cls.province, district=cls.district,
            city='Kathmandu', area='Baneshwor', monthly_rent=15000, status='approved'
        )

    def test_malformed_numeric_filters_do_not_crash(self):
        for value in ('abc', '-1', '9' * 50, '2.5'):
            with self.subTest(value=value):
                response = self.client.get(reverse('home'), {
                    'province': value, 'district': value, 'min_price': value, 'max_price': value
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_zero_maximum_rent_is_applied(self):
        response = self.client.get(reverse('home'), {'max_price': '0'})
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_search_filter_and_pagination_retain_parameters(self):
        for index in range(10):
            Listing.objects.create(
                owner=self.owner, title=f'Sunny flat {index}', description=self.listing.description,
                property_type='flat', province=self.province, district=self.district,
                city='Kathmandu', area='Baneshwor', monthly_rent=16000 + index, status='approved'
            )
        response = self.client.get(reverse('home'), {'q': 'Sunny', 'sort': 'price_low', 'page': '2'})
        self.assertEqual(response.context['page_obj'].paginator.count, 11)
        self.assertEqual(len(response.context['listings']), 2)
        self.assertIn('q=Sunny', response.context['query_string'])
        self.assertNotIn('page=', response.context['query_string'])

    def test_invalid_district_request_returns_json(self):
        response = self.client.get(reverse('load_districts'), {'province_id': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['districts'], [])

    def test_missing_location_fields_show_form_errors(self):
        form = ListingForm(data={'title': 'A flat', 'description': self.listing.description})
        self.assertFalse(form.is_valid())
        self.assertIn('district', form.errors)
        self.assertIn('province', form.errors)

    def test_fake_image_content_is_rejected(self):
        fake = SimpleUploadedFile('fake.jpg', b'not an image', content_type='image/jpeg')
        form = ListingImageEditForm(files=MultiValueDict({'new_images': [fake]}))
        self.assertFalse(form.is_valid())
        self.assertIn('new_images', form.errors)

    def test_excess_images_do_not_save_listing_edits(self):
        ListingImage.objects.bulk_create([
            ListingImage(listing=self.listing, image=f'existing-{index}.jpg') for index in range(15)
        ])
        ListingDocument.objects.create(
            listing=self.listing, citizenship_front='front.jpg', citizenship_back='back.jpg',
            lalpurja='land.jpg', selfie_with_citizenship='selfie.jpg'
        )
        self.client.force_login(self.owner)
        response = self.client.post(reverse('edit_listing', args=[self.listing.pk]), {
            'title': 'Changed title', 'description': self.listing.description,
            'property_type': 'flat', 'province': self.province.pk, 'district': self.district.pk,
            'city': 'Kathmandu', 'area': 'Baneshwor', 'monthly_rent': 15000,
            'security_deposit': 0, 'furnished_status': 'unfurnished', 'new_images': uploaded_photo()
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'maximum 15 images')
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Sunny flat')
        self.assertEqual(self.listing.status, 'approved')

    def test_detail_sets_csrf_cookie_and_phone_reveal_works(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('listing_detail', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', client.cookies)
        response = client.post(reverse('reveal_phone', args=[self.listing.pk]),
                               HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.json()['phone'], self.owner.phone)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.views_count, 1)

    def test_demo_replacement_is_scoped_and_repeatable(self):
        demo = ListingImage.objects.create(
            listing=self.listing, image='listings/1/images/Animated_Forest.png', is_primary=True
        )
        custom = ListingImage.objects.create(listing=self.listing, image='my-own-room.jpg')
        output = StringIO()
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            call_command('replace_demo_images', stdout=output)
            demo.refresh_from_db()
            self.assertTrue(demo.image.name.endswith('Animated_Forest.png'))
            call_command('replace_demo_images', apply=True, stdout=output)
            demo.refresh_from_db()
            self.assertIn('sample-property-', demo.image.name)
            self.assertTrue(demo.is_primary)
            self.assertTrue(demo.image.storage.exists(demo.image.name))
            call_command('replace_demo_images', apply=True, stdout=output)
            self.assertIn('Replaced 0 demo images.', output.getvalue())
            custom.refresh_from_db()
            self.assertEqual(custom.image.name, 'my-own-room.jpg')
