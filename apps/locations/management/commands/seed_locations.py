from django.core.management.base import BaseCommand
from apps.locations.models import Province, District


NEPAL_LOCATIONS = {
    "Koshi Province": [
        "Bhojpur", "Dhankuta", "Ilam", "Jhapa", "Khotang", "Morang",
        "Okhaldhunga", "Panchthar", "Sankhuwasabha", "Solukhumbu",
        "Sunsari", "Taplejung", "Terhathum", "Udayapur"
    ],
    "Madhesh Province": [
        "Bara", "Dhanusha", "Mahottari", "Parsa", "Rautahat",
        "Saptari", "Sarlahi", "Siraha"
    ],
    "Bagmati Province": [
        "Bhaktapur", "Chitwan", "Dhading", "Dolakha", "Kathmandu",
        "Kavrepalanchok", "Lalitpur", "Makwanpur", "Nuwakot",
        "Ramechhap", "Rasuwa", "Sindhuli", "Sindhupalchok"
    ],
    "Gandaki Province": [
        "Baglung", "Gorkha", "Kaski", "Lamjung", "Manang", "Mustang",
        "Myagdi", "Nawalpur", "Parbat", "Syangja", "Tanahun"
    ],
    "Lumbini Province": [
        "Arghakhanchi", "Banke", "Bardiya", "Dang", "Gulmi",
        "Kapilvastu", "Parasi", "Palpa", "Pyuthan", "Rolpa",
        "Rukum East", "Rupandehi"
    ],
    "Karnali Province": [
        "Dailekh", "Dolpa", "Humla", "Jajarkot", "Jumla",
        "Kalikot", "Mugu", "Rukum West", "Salyan", "Surkhet"
    ],
    "Sudurpashchim Province": [
        "Achham", "Baitadi", "Bajhang", "Bajura", "Dadeldhura",
        "Darchula", "Doti", "Kailali", "Kanchanpur"
    ],
}


class Command(BaseCommand):
    help = "Seed Nepal provinces and districts"

    def handle(self, *args, **kwargs):
        for province_name, districts in NEPAL_LOCATIONS.items():
            province, _ = Province.objects.get_or_create(name=province_name)

            for district_name in districts:
                District.objects.get_or_create(
                    province=province,
                    name=district_name
                )

        self.stdout.write(
            self.style.SUCCESS("Nepal provinces and districts seeded successfully.")
        )