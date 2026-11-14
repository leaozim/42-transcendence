import re
import secrets
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps
from srcs_user.models import User
from django.http import Http404

def find_one(id):
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        raise Http404(f"User with ID {id} does not exist.")

def find_one_intra(id_42):
    try:
        return User.objects.get(id_42=id_42)
    except User.DoesNotExist:
        raise Http404(f"User with ID {id_42} does not exist.")

def find_all():
    return User.objects.all()

def update(user_id, new_user):
    try:
        user = User.objects.get(id=user_id)
        user = new_user
        user.save()
    except User.DoesNotExist:
        raise Http404("User does not exist")

def delete_one(id):
    try:
        user = User.objects.get(id=id)
        user.delete()
    except User.DoesNotExist:
        raise Http404(f"User with ID {id} does not exist.")

def compute_mmr_points(user_id, points):
    try:
        user = User.objects.get(id=user_id)
        user.mmr += points
        user.save()
        return user
    except User.DoesNotExist:
        raise Http404(f"User with ID {user_id} does not exist.")


def get_validated_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404(f"User with ID {user_id} does not exist.")


# --- Avatars -------------------------------------------------------------------
#
# Uploaded images are never stored as received: they are decoded, rotated
# according to their EXIF orientation, cropped to a square and re-encoded as a
# JPEG. This bounds their size, strips metadata (e.g. GPS) and guarantees that
# whatever is served from MEDIA_URL is a plain image.

AVATAR_DIR = "avatars"
AVATAR_SIZE = 256
MAX_AVATAR_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_AVATAR_PIXELS = 40_000_000
ALLOWED_AVATAR_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}
# Transparent areas are filled with the site background colour (#000012).
AVATAR_BACKGROUND = (0, 0, 18)
_UPLOADED_AVATAR_NAME = re.compile(r"^%s/[0-9]+-[0-9a-f]{16}\.jpg$" % AVATAR_DIR)


def process_avatar(file) -> bytes:
    """Return ``file`` as a AVATAR_SIZE x AVATAR_SIZE JPEG."""
    file.seek(0)
    with Image.open(file) as image:
        if image.width * image.height > MAX_AVATAR_PIXELS:
            raise ValueError("Image has too many pixels")
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA", "PA") or "transparency" in image.info:
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, AVATAR_BACKGROUND)
            background.paste(image, mask=image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image = ImageOps.fit(
            image, (AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS
        )
        output = BytesIO()
        image.save(output, "JPEG", quality=88, optimize=True)
    return output.getvalue()


def _uploaded_avatar_name(url):
    """Storage name of an avatar previously uploaded by a user, else None."""
    if not url or not url.startswith(settings.MEDIA_URL):
        return None
    name = url[len(settings.MEDIA_URL):]
    return name if _UPLOADED_AVATAR_NAME.match(name) else None


def delete_uploaded_avatar(url):
    name = _uploaded_avatar_name(url)
    if name and default_storage.exists(name):
        default_storage.delete(name)


def save_avatar(user, file) -> str:
    """Store ``file`` as the user's avatar and return its URL."""
    data = process_avatar(file)
    # A new random name on every upload also defeats stale browser caches.
    name = default_storage.save(
        f"{AVATAR_DIR}/{user.pk}-{secrets.token_hex(8)}.jpg", ContentFile(data)
    )
    previous = user.avatar
    user.avatar = default_storage.url(name)
    user.save(update_fields=["avatar"])
    delete_uploaded_avatar(previous)
    return user.avatar
