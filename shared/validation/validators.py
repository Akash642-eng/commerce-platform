from fastapi import HTTPException


def validate_required_fields(
    payload: dict,
    required_fields: list
):

    missing = []

    for field in required_fields:

        if field not in payload:

            missing.append(field)

    if missing:

        raise HTTPException(
            status_code=400,
            detail=f"Missing fields: {', '.join(missing)}"
        )