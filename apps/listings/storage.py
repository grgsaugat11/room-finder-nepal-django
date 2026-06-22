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

        return f"{result['public_id']}.{result.get('format', '')}".rstrip(".")

    def exists(self, name):
        return False

    def url(self, name):
        video_extensions = ('.mp4', '.mov', '.avi', '.webm', '.mkv')

        if str(name).lower().endswith(video_extensions) or 'videos/' in str(name):
            resource_type = "video"
        else:
            resource_type = "image"

        url, options = cloudinary_url(
            name,
            resource_type=resource_type,
            secure=True
        )
        return url

    def delete(self, name):
        cloudinary.uploader.destroy(
            name,
            resource_type="auto",
            invalidate=True
        )