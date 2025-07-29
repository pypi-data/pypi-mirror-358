from .models import Subject


def get_cookie_name(instance: Subject) -> str:
    """Get cookie name."""
    return f"help_rating_{instance.pk}"


def get_cookie_replacement() -> str:
    """Get cookie pattern replacement."""
    return "SUBJECT_ID"


def get_cookie_pattern() -> str:
    """Get cookie pattern."""
    return "help_rating_" + get_cookie_replacement()
