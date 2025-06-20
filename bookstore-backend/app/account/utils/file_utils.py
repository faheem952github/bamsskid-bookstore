# app/utils/file_utils.py
import uuid
from datetime import datetime


def generate_unique_filename(filename: str, prefix: str = None) -> str:
    extension = filename.split(".")[-1]
    unique_name = f"{prefix}_{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"

    if prefix:
        # Ensure the prefix doesn't already include the word you're adding (e.g., 'Business_logo_')
        if not unique_name.startswith(prefix):
            return f"{prefix}_{unique_name}"

    return unique_name
