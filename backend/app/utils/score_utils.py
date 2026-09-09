from decimal import Decimal, InvalidOperation

SCORE_MAX = Decimal("9999999999.99999")
SCORE_UNIT = Decimal("0.00001")


def normalize_score(value):
    """Validate without rounding; Decimal is the internal score representation."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("score must be a JSON number")
    try:
        score = Decimal(str(value))
        if not score.is_finite() or abs(score) > SCORE_MAX:
            raise ValueError("score is outside Numeric(15, 5)")
        if score != score.quantize(SCORE_UNIT):
            raise ValueError("score must have at most five decimal places")
    except InvalidOperation as exc:
        raise ValueError("invalid score") from exc
    return score
