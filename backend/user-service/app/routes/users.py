from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app import schemas

from app.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


@router.get(
    "/",
    response_model=list[schemas.UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(
        models.User
    ).all()

    return users


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse
)
def update_user(
    user_id: int,
    updated_user: schemas.UserUpdate,
    db: Session = Depends(get_db)
):

    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.name = updated_user.name
    user.email = updated_user.email
    user.password = hash_password(
        updated_user.password
    )

    db.commit()

    db.refresh(user)

    return user


@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)

    db.commit()

    return {
        "message": "User deleted successfully"
    }