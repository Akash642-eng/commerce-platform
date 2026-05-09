from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.database import get_db

from app import models
from app import schemas

from app.security import get_current_user
from app.security import hash_password

from app.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# --------------------------------
# CREATE USER
# --------------------------------
@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED
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


    # --------------------------------
    # EMAIL ALREADY EXISTS
    # --------------------------------
    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )


    # --------------------------------
    # CREATE NEW USER
    # --------------------------------
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(
            user.password
        )
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# --------------------------------
# GET ALL USERS
# --------------------------------
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

#----------------------
# GET MY PROFILE
#----------------------

@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_my_profile(
    current_user: models.User = Depends(
        get_current_user
    )
):
    return current_user

# --------------------------------
# GET USER BY ID
# --------------------------------
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


    # --------------------------------
    # USER NOT FOUND
    # --------------------------------
    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# --------------------------------
# GET CURRENT USER
# --------------------------------
@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_current_logged_in_user(
    current_user: models.User = Depends(
        get_current_user
    )
):

    return current_user


# --------------------------------
# UPDATE USER
# --------------------------------
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


    # --------------------------------
    # USER NOT FOUND
    # --------------------------------
    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


    # --------------------------------
    # UPDATE NAME
    # --------------------------------
    if updated_user.name is not None:

        user.name = updated_user.name


    # --------------------------------
    # UPDATE EMAIL
    # --------------------------------
    if updated_user.email is not None:

        existing_email = db.query(
            models.User
        ).filter(
            models.User.email == updated_user.email,
            models.User.id != user_id
        ).first()

        if existing_email:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        user.email = updated_user.email


    # --------------------------------
    # UPDATE PASSWORD
    # --------------------------------
    if updated_user.password is not None:

        user.hashed_password = hash_password(
            updated_user.password
        )


    db.commit()

    db.refresh(user)

    return user


# --------------------------------
# DELETE USER
# --------------------------------
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


    # --------------------------------
    # USER NOT FOUND
    # --------------------------------
    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


    db.delete(user)

    db.commit()

    return {
        "message": "User deleted successfully"
    }

