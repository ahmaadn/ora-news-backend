import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.utils import exceptions
from app.utils.common import ErrorCode

UPLOAD_DIRECTORY = Path("static/img")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def validate_file_image(file: UploadFile):
    allowed_extensions = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=exceptions.FormatFileNotAllowedError(
                "Invalid file type. Only JPG and PNG are allowed.",
                error_code=ErrorCode.FORMAT_IMAGE_NOT_ALLOWED,
            ).dump(),
        )


def _generate_random_filename(file: UploadFile) -> str:
    """
    Generates a random filename with the same extension as the original file.
    """
    file_extension = file.filename.split(".")[-1]
    return f"{uuid.uuid4().hex}.{file_extension}"


async def handle_upload_image(file: UploadFile):
    validate_file_image(file)

    filename = _generate_random_filename(file)
    file_path = UPLOAD_DIRECTORY / filename

    try:
        content = await file.read()
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {e!s}",
        ) from e
    return filename, file_path
