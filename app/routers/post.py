from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.get('/', response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user), limit:int = 10, skip:int=0, search:Optional[str] = ''):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""Insert into posts (title, content, published) values (%s, %s, %s) returning * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute(f"""select * from posts where id = %s returning *""", (str(id)))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"id: {id} not found")
    return post

@router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute(f"""Delete from posts where id = %s returning *""", (str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"id: {id} not found")
    if current_user.id != post.user_id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Not allowed to remove post")

    post_query.delete(synchronize_session=False)
    db.commit()

    return post

@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, post1: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""", (post.title, post.content, post.published, id))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"id: {id} not found")
    if current_user.id != post.user_id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Not allowed to update post")
    post_query.update(post1.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()