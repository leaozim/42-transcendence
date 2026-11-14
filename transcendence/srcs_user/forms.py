from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from srcs_user.services import (
    ALLOWED_AVATAR_FORMATS,
    MAX_AVATAR_PIXELS,
    MAX_AVATAR_UPLOAD_BYTES,
)


class AvatarField(forms.ImageField):
    """Image upload limited in size, pixel count and format (JPEG/PNG/GIF/WebP)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("label", _("Avatar"))
        kwargs.setdefault(
            "widget",
            forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/gif,image/webp"}
            ),
        )
        super().__init__(**kwargs)

    def to_python(self, data):
        if data and getattr(data, "size", 0) > MAX_AVATAR_UPLOAD_BYTES:
            raise ValidationError(
                _("The image is too large (maximum %(size)s MB).")
                % {"size": MAX_AVATAR_UPLOAD_BYTES // (1024 * 1024)},
                code="file_too_large",
            )
        # Django opens and verifies the file with Pillow here.
        uploaded = super().to_python(data)
        if uploaded is None:
            return None
        image = uploaded.image
        if image.format not in ALLOWED_AVATAR_FORMATS:
            raise ValidationError(
                _("Use a JPEG, PNG, GIF or WebP image."), code="invalid_format"
            )
        if image.width * image.height > MAX_AVATAR_PIXELS:
            raise ValidationError(
                _("The image dimensions are too large."), code="too_many_pixels"
            )
        return uploaded


class AvatarUploadForm(forms.Form):
    avatar = AvatarField(required=True)
