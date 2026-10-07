from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.listings.models import ListingImage


# Only the original sample wallpapers are replaced; landlord uploads stay intact.
DEMO_PHOTOS = {
    '8032673-1328569404-73353.jpg': 'apartment.jpg',
    '3769f793ac41c56746644ff0882eac29.jpg': 'living-room.jpg',
    '309405-haikyuu-wallpaper-1920x1080-for-macbook.jpg': 'bedroom.jpg',
    '1695580909186.jpg': 'kitchen.jpg',
    'asuke-hypebeast.jpg': 'home-exterior.jpg',
    'Animated_Forest.png': 'home-exterior.jpg',
    'astronaut-cat-moon-digital-art-4k-wallpaper.jpg': 'living-room.jpg',
    'back1.jpg': 'house.jpg',
    'bridge_of_spirits.png': 'kitchen.jpg',
    'Cherry_Blossom_Sea_Anime_Scenery_Wallpaper_iPhone_Phone_4k_1530f.jpg': 'bedroom.jpg',
}


class Command(BaseCommand):
    help = 'Replace original demo wallpapers with bundled real property sample photos.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Save replacements; otherwise preview only.')

    def handle(self, *args, **options):
        count = 0
        for image in ListingImage.objects.all():
            replacement = DEMO_PHOTOS.get(Path(image.image.name).name)
            if not replacement:
                continue
            self.stdout.write(f'Listing {image.listing_id}, image {image.pk}: {replacement}')
            if options['apply']:
                source = settings.BASE_DIR / 'static' / 'images' / 'properties' / replacement
                with source.open('rb') as photo:
                    image.image.save(f'sample-property-{replacement}', File(photo), save=True)
            count += 1
        action = 'Replaced' if options['apply'] else 'Would replace'
        self.stdout.write(self.style.SUCCESS(f'{action} {count} demo images.'))
