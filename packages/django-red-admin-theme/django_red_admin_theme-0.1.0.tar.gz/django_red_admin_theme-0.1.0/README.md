Django Red Admin Theme
A Django admin theme that applies a red color scheme with custom fonts and sizes.
Installation
pip install django-red-admin-theme

Usage

Add "django_red_admin_theme" to INSTALLED_APPS in your Django settings.py:

INSTALLED_APPS = [
    'django_red_admin_theme',
    'django.contrib.admin',
    # ... other apps
]


Run python manage.py collectstatic to copy the static files to your project’s static directory.

The red theme will automatically apply to your Django admin interface.


License
MIT License