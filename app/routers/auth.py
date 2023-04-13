from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

@router.post('/', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Credentials not right")

    if not utils.verify_hash(user_credentials.password, user.password):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Credentials not right")
    
    acces_token = oauth2.create_acces_token(data = {'user_id': user.id})
    return {'acces_token':acces_token, 'token_type':'bearer'}