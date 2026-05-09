from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from ..database import get_db

from .. import models
from .. import schemas


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# --------------------------------
# CREATE CATEGORY
# --------------------------------

@router.post(
    "/",
    response_model=schemas.CategoryResponse
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):

    new_category = models.Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)

    db.commit()

    db.refresh(new_category)

    return new_category


# --------------------------------
# GET ALL CATEGORIES
# --------------------------------

@router.get(
    "/",
    response_model=list[schemas.CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):

    return db.query(models.Category).all()