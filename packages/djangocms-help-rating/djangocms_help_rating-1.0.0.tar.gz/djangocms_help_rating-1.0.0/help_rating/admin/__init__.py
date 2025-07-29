import statistics

from django.contrib import admin
from django.db.models import Avg, Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models import Feedback, Subject


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["subject", "view_on_page", "score", "modified", "remote_addr"]
    readonly_fields = [
        "subject",
        "view_on_page",
        "remote_addr",
        "browser_fingerprint",
        "modified",
        "score",
    ]
    list_filter = ["subject__plugin", "modified"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_("On the page"))
    def view_on_page(self, obj):
        return (
            format_html(
                '<a href="{}?help_rating={}#help-rating-{}" target="_top">{}</a>',
                obj.subject.last_plugin.page.get_absolute_url(),
                obj.subject.pk,
                obj.subject.pk,
                obj.subject.last_plugin.page,
            )
            if obj.subject.last_plugin is not None and obj.subject.last_plugin.page is not None
            else ""
        )


class SubjectAdmin(admin.ModelAdmin):
    readonly_fields = ["last_plugin"]
    list_display = [
        "view_subject",
        "view_on_page",
        "view_score_arithmetic_mean",
        "view_score_median",
        "view_score_number",
        "view_addresses_number",
    ]
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_("Voting content"))
    def view_subject(self, obj):
        return obj.last_plugin

    @admin.display(description=_("On the page"))
    def view_on_page(self, obj):
        return (
            format_html(
                '<a href="{}?help_rating={}#help-rating-{}" target="_top">{}</a>',
                obj.last_plugin.page.get_absolute_url(),
                obj.pk,
                obj.pk,
                obj.last_plugin.page,
            )
            if obj.last_plugin is not None and obj.last_plugin.page is not None
            else ""
        )

    @admin.display(description=_("Number of votes"))
    def view_score_number(self, obj) -> int:
        return obj.feedback_set.count()

    @admin.display(description=_("Arithmetic mean"))
    def view_score_arithmetic_mean(self, obj) -> str:
        queryset = obj.feedback_set.values("subject").annotate(socre_avg=Avg("score"))
        return f"{queryset[0]['socre_avg']:.2f}" if len(queryset) else ""

    @admin.display(description=_("Median"))
    def view_score_median(self, obj) -> str:
        queryset = obj.feedback_set.values_list("score", flat=True)
        return f"{statistics.median(queryset):.2f}" if len(queryset) else ""

    @admin.display(description=_("Number of addresses"))
    def view_addresses_number(self, obj) -> int:
        return len(obj.feedback_set.values("remote_addr").annotate(remote_addr_count=Count("remote_addr")))


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Feedback, FeedbackAdmin)
