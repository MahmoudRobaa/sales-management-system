"""
Settings router.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("", response_model=List[schemas.SettingResponse])
def get_settings(db: Session = Depends(get_db)):
    return crud.get_settings(db)


@router.put("", response_model=List[schemas.SettingResponse])
def update_settings(settings: schemas.SettingsUpdate, db: Session = Depends(get_db)):
    return crud.update_settings(db, settings.settings)
