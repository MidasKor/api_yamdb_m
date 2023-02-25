"""Validating functions."""

import re

from django.utils import timezone


def genre_slug_check(slug):
    """Validate user provided slug.

    Args:
        slug (str): user's slug

    Returns:
        bool: whether given slug string mathes the pattern or not
    """
    return re.fullmatch((r"^[-a-zA-Z0-9_]+$"), slug)


def year_check(num):
    """Validate user provided year.

    Args:
        num (int): user prodided year for a title

    Returns:
        bool: whether given year valid or not (checking the given year
        not greater that the current one)
    """
    return timezone.now().year >= num
