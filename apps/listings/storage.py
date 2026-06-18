import uuid

from django.core.files.storage import Storage
from django.conf import settings

import cloudinary.uploader
from cloudinary.utils import cloudinary_url


class CloudinaryMediaStorage(Storage):
    def _save(self, name, content):
        folder = getattr(settings, "CLOUDINARY_FOLDER", "room_finder")

        # extension = name.split(".")[-1] if "." in name else ""
        base_name = name.rsplit(".", 1)[0]

        unique_name = f"{base_name}_{uuid.uuid4().hex[:10]}"

        result = cloudinary.uploader.upload(
            content,
            folder=folder,
            public_id=unique_name,
            resource_type="auto",
            overwrite=False,
        )

        return result["public_id"]

    def exists(self, name):
        return False

    def url(self, name):
        url, options = cloudinary_url(
            name,
            resource_type="auto",
            secure=True
        )
        return url

    def delete(self, name):
        cloudinary.uploader.destroy(
            name,
            resource_type="auto",
            invalidate=True
        )