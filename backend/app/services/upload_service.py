"""
Upload storage service.

Generates a unique filename and stores
the uploaded image in app/uploads.
"""

import os
import shutil
import uuid


UPLOAD_DIRECTORY = "app/uploads"


def save_uploaded_file(upload_file):
    """
    Save an uploaded file using a unique filename.

    Returns:
        (unique_filename, file_path)
    """

    os.makedirs(
        UPLOAD_DIRECTORY,
        exist_ok=True,
    )

    original_filename = (
        upload_file.filename or ""
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        unique_filename,
    )

    with open(
        file_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            upload_file.file,
            buffer,
        )

    return (
        unique_filename,
        file_path,
    )