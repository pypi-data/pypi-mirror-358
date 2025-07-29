import logging
from typing import Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.plugin_rendering import PluginContext
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from .constants import RATINGS
from .models import Plugin
from .utils import get_cookie_name, get_cookie_pattern, get_cookie_replacement


@plugin_pool.register_plugin
class RatingPlugin(CMSPluginBase):
    model = Plugin
    name = _("Help Rating")
    render_template = "help_rating/rating-plugin.html"
    text_enabled = True

    def render(self, context: PluginContext, instance: Plugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)  # type: ignore[misc]
        context["ratings"] = RATINGS
        context["cookie_pattern"] = get_cookie_pattern()
        context["cookie_replacement"] = get_cookie_replacement()
        answered = context["request"].COOKIES.get(get_cookie_name(instance))
        if answered is not None:
            try:
                context["answered"] = int(answered)
            except ValueError:
                pass
        namespace = getattr(settings, "HELP_RATING_PATH_NAMESPACE", "help_rating")
        try:
            context["save_score_url"] = reverse(f"{namespace}:save_score")
        except NoReverseMatch as msg:
            logging.error(msg)
        return context
