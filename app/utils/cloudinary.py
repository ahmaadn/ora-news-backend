# libs/cloudinary.py
from uuid import UUID

import cloudinary
import cloudinary.uploader

from app.core.config import get_settings

cloudinary.config(
    cloud_name=get_settings().CLOUDINARY_CLOUD_NAME,
    api_key=get_settings().CLOUDINARY_API_KEY,
    api_secret=get_settings().CLOUDINARY_API_SECRET,
)


async def upload_image_to_cloudinary(file, news_id: UUID):
    return cloudinary.uploader.upload(
        file, folder="oranews", public_id=str(news_id), overwrite=True, resource_type="image"
    )
