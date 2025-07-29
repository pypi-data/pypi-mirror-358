import hashlib
import logging

from django.http import HttpRequest, JsonResponse
from django.views.generic import View

from .constants import VALID_VALUES
from .models import Feedback, Subject
from .utils import get_cookie_name

logger = logging.getLogger(__name__)


class InvalidData(Exception):
    """Invalid data exception."""


class SaveFeedback(View):
    """Save Feedback view."""

    def _save_score(self, request: HttpRequest):
        """Save score."""
        if not request.POST.get("subject_id"):
            raise InvalidData()
        score = int(request.POST.get("score"))
        if score not in VALID_VALUES:
            raise InvalidData()
        subject = Subject.objects.get(pk=request.POST.get("subject_id"))
        headers = (
            "accept-encoding",
            "accept-language",
            "user-agent",
        )
        content = "\n".join([f"{header}: {request.headers.get(header)}" for header in headers])
        logger.debug(content)
        instance, created = Feedback.objects.get_or_create(
            subject=subject,
            remote_addr=request.META["REMOTE_ADDR"],
            browser_fingerprint=hashlib.sha256(content.encode()).hexdigest(),
            defaults={"score": score},
        )
        if created:
            logger.debug(f"Instance {instance.pk} created with score {score}.")
        if not created and instance.score != score:
            instance.score = score
            instance.save()
            logger.debug(f"Instance {instance.pk} updated to score {score}.")
        return get_cookie_name(subject), instance.score

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            cookie_name, cookie_value = self._save_score(request)
            data = {"status": "ok"}
        except (InvalidData, TypeError, ValueError, Subject.DoesNotExist):
            cookie_name, cookie_value = None, None
            data = {"status": "failure"}
        response = JsonResponse(data)
        if cookie_name is not None:
            response.set_cookie(cookie_name, cookie_value)
        return response
