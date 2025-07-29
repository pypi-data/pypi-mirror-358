from copy import deepcopy

from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    def __str__(self):
        plugin = self.last_plugin
        return "-" if plugin is None else str(plugin)

    class Meta:
        verbose_name = _("Vote summarization")
        verbose_name_plural = _("Vote summarizations")

    @property
    def last_plugin(self):
        return self.plugin_set.last()


class Plugin(CMSPlugin):
    """Rating model."""

    subject = models.ForeignKey(
        Subject, editable=False, on_delete=models.SET_NULL, null=True, verbose_name=_("Voting content")
    )
    name = models.CharField(verbose_name=_("Subject name"), max_length=255, help_text=_("Subject of evaluation."))

    old_id: int = None

    def __str__(self):
        return self.name

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
            if k == "cmsplugin_ptr_id":
                result.old_id = deepcopy(v, memo)
        return result

    def save(self, *args, **kwarg):
        if self.old_id:
            if self.subject is None:
                self.subject, _ = Subject.objects.get_or_create(plugin=self.old_id)
        super().save(*args, **kwarg)
        if self.subject is None:
            self.subject = Subject.objects.create(plugin=self)
            self.save()


class Feedback(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_("Voting content"))
    remote_addr = models.GenericIPAddressField(_("Remote address"))
    browser_fingerprint = models.CharField(_("Browser fingerprint"), max_length=64)
    modified = models.DateTimeField(_("Last modified at"), auto_now=True)
    score = models.SmallIntegerField(_("Score"))

    class Meta:
        verbose_name = _("User voting")
        verbose_name_plural = _("User votings")
        unique_together = ["subject", "remote_addr", "browser_fingerprint"]

    def __str__(self):
        return str(self.subject)
