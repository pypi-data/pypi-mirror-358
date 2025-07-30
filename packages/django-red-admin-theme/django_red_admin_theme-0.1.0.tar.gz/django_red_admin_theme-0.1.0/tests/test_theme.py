from django.test import TestCase

class RedAdminThemeTest(TestCase):
    def test_package_import(self):
        try:
            import django_red_admin_theme
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import django_red_admin_theme")