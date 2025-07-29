from cms.models import PageContent
from django.dispatch import receiver
from djangocms_versioning.constants import OPERATION_ARCHIVE, OPERATION_DRAFT, OPERATION_PUBLISH, OPERATION_UNPUBLISH
from djangocms_versioning.signals import post_version_operation

from .models import Subject


@receiver(post_version_operation, sender=PageContent)
def delete_subject_without_plugin(*args, **kwargs):
    if kwargs["operation"] in (OPERATION_ARCHIVE, OPERATION_DRAFT, OPERATION_PUBLISH, OPERATION_UNPUBLISH):
        Subject.objects.filter(plugin__isnull=True).delete()
