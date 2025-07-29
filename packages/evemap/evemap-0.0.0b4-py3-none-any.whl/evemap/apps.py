from django.apps import AppConfig

from . import __version__


class EveMapConfig(AppConfig):
    name = "evemap"
    label = "evemap"
    verbose_name = f"evemap v{__version__}"
