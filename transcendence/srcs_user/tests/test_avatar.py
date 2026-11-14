import importlib
import os
import re
import shutil
import tempfile
from io import BytesIO
from unittest import mock

from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from srcs_user import services
from srcs_user.models import User, default_avatar

MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"
PASSWORD = "c0rrect-Horse-battery"


def image_file(name="avatar.png", fmt="PNG", size=(400, 300), mode="RGB", color=(200, 30, 30), exif=None):
    image = Image.new(mode, size, color)
    output = BytesIO()
    kwargs = {"exif": exif} if exif is not None else {}
    image.save(output, fmt, **kwargs)
    return SimpleUploadedFile(name, output.getvalue(), content_type=f"image/{fmt.lower()}")


def open_result(data):
    return Image.open(BytesIO(data))


class MediaRootMixin:
    def setUp(self):
        super().setUp()
        self.media_root = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def stored_files(self):
        folder = os.path.join(self.media_root, services.AVATAR_DIR)
        return sorted(os.listdir(folder)) if os.path.isdir(folder) else []


class ProcessAvatarTestCase(TestCase):
    def test_output_is_square_jpeg(self):
        result = open_result(services.process_avatar(image_file(size=(800, 400))))

        self.assertEqual(result.format, "JPEG")
        self.assertEqual(result.size, (services.AVATAR_SIZE, services.AVATAR_SIZE))

    def test_transparency_is_filled_with_site_background(self):
        upload = image_file(mode="RGBA", color=(255, 0, 0, 0))

        pixel = open_result(services.process_avatar(upload)).getpixel((5, 5))

        for channel, expected in zip(pixel, services.AVATAR_BACKGROUND):
            self.assertAlmostEqual(channel, expected, delta=6)

    def test_exif_orientation_is_applied(self):
        # Left half red, right half blue; orientation 6 = "rotate 90 degrees clockwise".
        image = Image.new("RGB", (300, 300), (255, 0, 0))
        image.paste((0, 0, 255), (150, 0, 300, 300))
        exif = Image.Exif()
        exif[0x0112] = 6
        output = BytesIO()
        image.save(output, "JPEG", exif=exif)

        result = open_result(services.process_avatar(BytesIO(output.getvalue())))

        top, bottom = result.getpixel((128, 20)), result.getpixel((128, 236))
        self.assertGreater(top[0], 200)  # red ends up on top
        self.assertGreater(bottom[2], 200)  # blue at the bottom

    def test_too_many_pixels_is_rejected(self):
        with mock.patch.object(services, "MAX_AVATAR_PIXELS", 100):
            with self.assertRaises(ValueError):
                services.process_avatar(image_file(size=(20, 20)))


class SaveAvatarTestCase(MediaRootMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("player", "player@example.com", PASSWORD)

    def test_save_stores_file_and_url(self):
        url = services.save_avatar(self.user, image_file())

        self.assertRegex(url, r"^/media/avatars/%d-[0-9a-f]{16}\.jpg$" % self.user.pk)
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, url)
        self.assertEqual(self.stored_files(), [url.rsplit("/", 1)[1]])

    def test_new_upload_replaces_previous_file(self):
        first = services.save_avatar(self.user, image_file())
        second = services.save_avatar(self.user, image_file(color=(0, 200, 0)))

        self.assertNotEqual(first, second)
        self.assertEqual(self.stored_files(), [second.rsplit("/", 1)[1]])

    def test_only_uploaded_avatars_are_deleted(self):
        victim = os.path.join(self.media_root, "keep.txt")
        with open(victim, "w") as f:
            f.write("x")
        for url in [
            default_avatar(),
            "https://cdn.intra.42.fr/users/someone.jpg",
            "/media/keep.txt",
            "/media/avatars/../keep.txt",
            "",
            None,
        ]:
            services.delete_uploaded_avatar(url)

        self.assertTrue(os.path.exists(victim))


class AvatarUploadViewTestCase(MediaRootMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("player", "player@example.com", PASSWORD)
        self.client.force_login(self.user, backend=MODEL_BACKEND)
        self.url = reverse("srcs_user:avatar")

    def test_upload_returns_new_url_which_is_served(self):
        response = self.client.post(self.url, {"avatar": image_file()})

        self.assertEqual(response.status_code, 200)
        avatar_url = response.json()["avatar"]
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, avatar_url)
        served = self.client.get(avatar_url)
        self.assertEqual(served.status_code, 200)
        self.assertEqual(served["Content-Type"], "image/jpeg")
        served.close()

    def test_non_image_is_rejected(self):
        fake = SimpleUploadedFile("avatar.png", b"<script>alert(1)</script>", content_type="image/png")

        response = self.client.post(self.url, {"avatar": fake})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(self.stored_files(), [])

    def test_unsupported_format_is_rejected(self):
        response = self.client.post(self.url, {"avatar": image_file("avatar.bmp", fmt="BMP")})

        self.assertEqual(response.status_code, 400)
        self.assertIn("JPEG, PNG, GIF or WebP", response.json()["error"])

    def test_too_large_file_is_rejected(self):
        with mock.patch("srcs_user.forms.MAX_AVATAR_UPLOAD_BYTES", 100):
            response = self.client.post(self.url, {"avatar": image_file()})

        self.assertEqual(response.status_code, 400)
        self.assertIn("too large", response.json()["error"])

    def test_missing_file_is_rejected(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_login_required(self):
        self.client.logout()

        response = self.client.post(self.url, {"avatar": image_file()})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stored_files(), [])


class SignUpAvatarTestCase(MediaRootMixin, TestCase):
    def signup(self, **extra):
        data = {
            "username": "newbie",
            "email": "newbie@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
            **extra,
        }
        return self.client.post(reverse("srcs_auth:signup"), data)

    def test_signup_form_accepts_files(self):
        response = self.client.get(reverse("srcs_auth:signup"))

        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'type="file" name="avatar"')

    def test_signup_with_avatar(self):
        self.signup(avatar=image_file())

        avatar = User.objects.get(username="newbie").avatar
        self.assertTrue(avatar.startswith("/media/avatars/"))
        self.assertEqual(len(self.stored_files()), 1)

    def test_signup_without_avatar_uses_local_default(self):
        self.signup()

        self.assertEqual(User.objects.get(username="newbie").avatar, "/static/images/sloth.jpg")

    def test_signup_with_invalid_avatar_shows_error(self):
        fake = SimpleUploadedFile("avatar.png", b"not an image", content_type="image/png")

        response = self.signup(avatar=fake)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "invalid-feedback d-block")
        self.assertFalse(User.objects.filter(username="newbie").exists())


class DefaultAvatarTestCase(TestCase):
    def test_default_avatar_is_local(self):
        user = User.objects.create_user("player", "player@example.com", PASSWORD)

        self.assertEqual(user.avatar, "/static/images/sloth.jpg")

    def test_intra_user_without_picture_gets_local_default(self):
        user = User.objects.create_new_intra_user(
            {"id": 4242, "login": "marvin", "email": "m@42.fr", "image": {"link": None}}
        )

        self.assertEqual(user.avatar, "/static/images/sloth.jpg")

    def test_migration_replaces_old_cloudinary_default(self):
        migration = importlib.import_module("srcs_user.migrations.0003_local_default_avatar")
        old = User.objects.create_user("old", "o@example.com", PASSWORD)
        User.objects.filter(pk=old.pk).update(avatar=migration.OLD_DEFAULT_AVATAR)
        intra = User.objects.create_user("intra", "i@example.com", PASSWORD)
        User.objects.filter(pk=intra.pk).update(avatar="https://cdn.intra.42.fr/users/intra.jpg")

        migration.use_local_default_avatar(apps, None)

        old.refresh_from_db()
        intra.refresh_from_db()
        self.assertEqual(old.avatar, "/static/images/sloth.jpg")
        self.assertEqual(intra.avatar, "https://cdn.intra.42.fr/users/intra.jpg")


class PageAssetsAndLanguageTestCase(TestCase):
    EXTERNAL_ASSET = re.compile(r'<(?:script|img|link)\b[^>]*\b(?:src|href)="https?://', re.I)

    def setUp(self):
        self.user = User.objects.create_user("player", "player@example.com", PASSWORD)

    def test_pages_load_no_external_assets(self):
        pages = {"landing": self.client.get("/"), "signup": self.client.get(reverse("srcs_auth:signup"))}
        self.client.force_login(self.user, backend=MODEL_BACKEND)
        pages["home"] = self.client.get("/")

        for name, response in pages.items():
            with self.subTest(page=name):
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(self.EXTERNAL_ASSET.search(response.content.decode()))
                self.assertContains(response, "bootstrap-icons/font/bootstrap-icons.min.css")
                self.assertContains(response, "js/popper.min.js")

    def test_language_menu_before_and_after_login(self):
        for logged_in in (False, True):
            if logged_in:
                self.client.force_login(self.user, backend=MODEL_BACKEND)
            with self.subTest(logged_in=logged_in):
                response = self.client.get("/")
                self.assertContains(response, 'class="dropdown language-menu"')
                self.assertContains(response, f'action="{reverse("set_language")}"')
                self.assertContains(response, 'name="language" value="pt-br"')
                self.assertContains(response, 'name="language" value="en"')

    def test_switching_language(self):
        response = self.client.post(reverse("set_language"), {"language": "pt-br", "next": "/"}, follow=True)

        self.assertContains(response, "Ainda não tem conta?")
        self.assertContains(response, '<html lang="pt-br">')
        self.assertContains(response, "<b>PT-BR</b>")
        self.assertRegex(response.content.decode(), r'class="dropdown-item active"\s+lang="pt-br"')

    def test_portuguese_is_brazilian_portuguese(self):
        # Old "pt" cookies and pt-PT browsers get the Brazilian translation.
        self.client.cookies["django_language"] = "pt"
        self.assertContains(self.client.get("/"), '<html lang="pt-br">')
        self.client.cookies.pop("django_language")
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="pt-PT,pt;q=0.9")
        self.assertContains(response, "Cadastre-se")
        self.assertContains(response, "Português Brasileiro (PT-BR)")

    def test_home_places_avatar_in_circle(self):
        User.objects.filter(pk=self.user.pk).update(avatar="/media/avatars/1-0123456789abcdef.jpg")
        self.client.force_login(self.user, backend=MODEL_BACKEND)

        response = self.client.get("/")

        self.assertRegex(
            response.content.decode(),
            r'<div class="avatar-circle">\s*<img[^>]+avatar_frame\.png[^>]*>\s*'
            r'<img src="/media/avatars/1-0123456789abcdef\.jpg"[^>]*class="img-avatar"',
        )
