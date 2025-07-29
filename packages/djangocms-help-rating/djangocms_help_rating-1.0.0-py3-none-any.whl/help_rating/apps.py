from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _


def delete_subject_without_plugin(sender, **kwargs):
    from .models import Subject

    Subject.objects.filter(plugin__isnull=True).delete()


def dispatch_post_delete_signal(sender, **kwargs):
    from .models import Plugin, Subject

    if isinstance(sender, Plugin):
        Subject.objects.filter(plugin__isnull=True).delete()


class HelpRating(AppConfig):
    name = "help_rating"
    verbose_name = _("Help Rating")

    def ready(self):
        post_delete.connect(dispatch_post_delete_signal)
        if getattr(settings, "CMS_CONFIRM_VERSION4", False):
            from . import receivers  # noqa @UnusedImport
        else:
            from cms.signals import post_obj_operation, post_publish

            post_obj_operation.connect(delete_subject_without_plugin)
            post_publish.connect(delete_subject_without_plugin)
