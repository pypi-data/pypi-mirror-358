from __future__ import annotations

from django.conf import settings
from django.core.signals import setting_changed
from rest_framework.settings import perform_import

DEFAULTS = {
    # Base API policies
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework_channels.permissions.AllowAny',),
    'JSON_ENCODER_CLASS': None,
    # Generic action handler behavior
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_FILTER_BACKENDS': [],
    # Pagination
    'PAGE_SIZE': None,
    # Exception
    'EXCEPTION_HANDLER': (
        'rest_framework_channels.exceptions.debug_exception_handlers'
        if settings.DEBUG
        else 'rest_framework_channels.exceptions.production_exception_handlers'
    ),
}
# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'DEFAULT_PERMISSION_CLASSES',
    'JSON_ENCODER_CLASS',
    'DEFAULT_PAGINATION_CLASS',
    'DEFAULT_FILTER_BACKENDS',
    'EXCEPTION_HANDLER',
)


class APISettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'REST_FRAMEWORK_CHANNELS', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid API setting: '{attr}'")

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'REST_FRAMEWORK_CHANNELS':
        api_settings.reload()


setting_changed.connect(reload_api_settings)
