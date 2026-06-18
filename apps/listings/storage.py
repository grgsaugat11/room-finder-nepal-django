from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from cloudinary.uploader import upload, destroy
from cloudinary.utils import cloudinary_url


class CloudinaryMediaStorage(Storage):
    def _save(self, name, content):
        folder = getattr(settings, "CLOUDINARY_FOLDER", "room_finder")

        result = upload(
            content,
            folder=folder,
            public_id=name.rsplit(".", 1)[0],
            resource_type="auto",
            overwrite=True,
        )

        return result["public_id"]

    def exists(self, name):
        return False

    def url(self, name):
        url, _ = cloudinary_url(name, resource_type="auto")
        return url

    def delete(self, name):
        destroy(name, resource_type="auto")