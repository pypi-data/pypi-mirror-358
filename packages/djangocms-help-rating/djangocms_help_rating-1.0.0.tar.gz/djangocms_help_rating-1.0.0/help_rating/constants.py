from enum import IntEnum, unique
from typing import NamedTuple

from django.utils.translation import gettext_lazy as _


@unique
class ScoreType(IntEnum):
    NOT_AT_ALL = 10
    PARTIALLY = 20
    YES = 30


class ScoreItem(NamedTuple):
    """Score item."""

    value: ScoreType
    slug: str
    icon: str
    label: str


RATINGS = [
    ScoreItem(ScoreType.NOT_AT_ALL.value, "not-at-all", "help_rating/img/smiley-sad-fill.svg", _("Not at all")),
    ScoreItem(ScoreType.PARTIALLY.value, "partially", "help_rating/img/smiley-meh-fill.svg", _("Partially")),
    ScoreItem(ScoreType.YES.value, "yes", "help_rating/img/smiley-fill.svg", _("Yes")),
]


VALID_VALUES = [item.value for item in RATINGS]
