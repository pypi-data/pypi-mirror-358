from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class EveMapMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Map"),
            "fas fa-location-pin fa-fw",
            "evemap:index",
            navactive=["evemap:"],
        )

    def render(self, request):
        if request.user.has_perm("evemap.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return EveMapMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "evemap", r"^evemap/")
