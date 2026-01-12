"""Image data URI validation utilities."""

import base64
import re

# Constants
MAX_IMAGE_COUNT = 5
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = frozenset([
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
])

# Data URI pattern: data:[<media-type>][;base64],<data>
DATA_URI_PATTERN = re.compile(r"^data:([^;,]+)(?:;base64)?,(.+)$", re.DOTALL)


def validate_image_data_uris(image_data_uris: list[str] | None) -> list[str]:
    """
    Validate image data URIs for count, size, MIME type, and base64 integrity.

    Args:
        image_data_uris: List of base64 encoded image data URIs

    Returns:
        List of validation error messages (empty if all valid)
    """
    errors: list[str] = []

    if not image_data_uris:
        return errors

    # Check maximum count
    if len(image_data_uris) > MAX_IMAGE_COUNT:
        errors.append(
            f"Too many images: {len(image_data_uris)} provided, maximum {MAX_IMAGE_COUNT} allowed"
        )
        return errors  # Short-circuit if count exceeded

    for i, data_uri in enumerate(image_data_uris, start=1):
        # Validate format
        if not data_uri.startswith("data:"):
            errors.append(f"Image {i}: Invalid data URI format (must start with 'data:')")
            continue

        # Parse data URI
        match = DATA_URI_PATTERN.match(data_uri)
        if not match:
            errors.append(f"Image {i}: Malformed data URI structure")
            continue

        media_type = match.group(1).lower()
        base64_data = match.group(2)

        # Validate MIME type
        if media_type not in ALLOWED_MIME_TYPES:
            errors.append(
                f"Image {i}: Unsupported MIME type '{media_type}' "
                f"(allowed: PNG, JPEG, GIF, WebP)"
            )
            continue

        # Validate and decode base64
        try:
            image_bytes = base64.b64decode(base64_data)

            # Check size limit
            if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
                size_mb = len(image_bytes) / (1024 * 1024)
                errors.append(
                    f"Image {i}: Size {size_mb:.1f}MB exceeds maximum 5MB"
                )
        except Exception:
            errors.append(f"Image {i}: Invalid base64 encoding")

    return errors


def parse_data_uri(data_uri: str) -> tuple[str, bytes] | None:
    """
    Parse a data URI and return the media type and decoded bytes.

    Args:
        data_uri: Base64 encoded data URI

    Returns:
        Tuple of (media_type, decoded_bytes) or None if invalid
    """
    match = DATA_URI_PATTERN.match(data_uri)
    if not match:
        return None

    media_type = match.group(1)
    base64_data = match.group(2)

    try:
        image_bytes = base64.b64decode(base64_data)
        return media_type, image_bytes
    except Exception:
        return None
