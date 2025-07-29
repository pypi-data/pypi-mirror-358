"""App settings."""

import os
from pathlib import Path

from django.conf import settings

EXAMPLE_SETTING_ONE = getattr(settings, "EXAMPLE_SETTING_ONE", None)

DEBUG = getattr(settings, "DEBUG", False)

BASE_DIR = Path(__file__).resolve().parent
VITE_APP_DIR = os.path.join(BASE_DIR, "static/evemap/frontend")
STATIC_URL = "static/evemap/frontend"
STATICFILES_DIRS = [
    os.path.join(VITE_APP_DIR, ".vite"),
]
