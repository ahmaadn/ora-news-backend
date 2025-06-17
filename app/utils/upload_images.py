import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

UPLOAD_DIRECTORY = Path("static/img")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def _validate_file_type(file: UploadFile):
    allowed_extensions = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG and PNG are allowed.",
        )


def _generate_random_filename(file: UploadFile) -> str:
    """
    Generates a random filename with the same extension as the original file.
    """
    file_extension = file.filename.split(".")[-1]
    return f"{uuid.uuid4().hex}.{file_extension}"


async def handle_upload_image(file: UploadFile) -> str:
    _validate_file_type(file)

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
