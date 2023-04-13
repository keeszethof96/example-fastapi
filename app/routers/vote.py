from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/votes',
    tags=['Votes']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"vote not found")

    vote_query = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, models.Vote.post_id == vote.post_id )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise   HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f'id {current_user.id} already has voted')

        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {'message': 'succefully voted'}
    else:
        if not found_vote:
            raise   HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'vote doesnt exist')
        vote_query.delete()
        db.commit()
        return {'message': 'succefully deleted vote'}                    
