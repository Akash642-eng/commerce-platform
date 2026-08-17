ALLOWED_TRANSITIONS = {
    "CREATED": ["RESERVED", "FAILED"],
    "RESERVED": ["PAID", "FAILED"],
    "PAID": ["COMPLETED", "REFUNDED"],
    "COMPLETED": [],
    "FAILED": [],
    "REFUNDED": [],
    "CANCELLED": [],
}


FINAL_STATES = {
    "COMPLETED",
    "FAILED",
    "REFUNDED",
    "CANCELLED",
}


def can_transition(current: str, new: str) -> bool:
    """
    Returns True if the requested state transition is valid.
    """
    return new in ALLOWED_TRANSITIONS.get(current, [])


def is_final_state(state: str) -> bool:
    """
    Returns True if the order has reached a terminal state.
    """
    return state in FINAL_STATES


def get_allowed_transitions(state: str):
    """
    Returns all valid transitions for a given state.
    """
    return ALLOWED_TRANSITIONS.get(state, [])


def validate_transition(current: str, new: str):
    """
    Raises an exception if an invalid transition is attempted.
    """
    if not can_transition(current, new):
        raise ValueError(
            f"Invalid state transition: {current} -> {new}"
        )