ALLOWED_TRANSITIONS = {
    "CREATED": ["RESERVED", "FAILED"],
    "RESERVED": ["PAID", "FAILED"],
    "PAID": [],
    "FAILED": []
}


def can_transition(current, new):
    return new in ALLOWED_TRANSITIONS.get(current, [])