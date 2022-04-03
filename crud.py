from sqlalchemy.orm import Session
import random
import string
import models, schemas
import time
from typing import List

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 5000):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_tokens(db: Session, skip: int = 0, limit: int = 5000):
    return db.query(models.UserToken).offset(skip).limit(limit).all()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_token(db: Session, token: str):
    return db.query(models.UserToken).filter(models.UserToken.token == token).first()

def get_access_token(db: Session, token: str):
    return db.query(models.AccessToken).filter(models.AccessToken.token == token).first()

def get_access_token_request(db: Session, grant_url: str):
    return db.query(models.AccessTokenRequest).filter(models.AccessTokenRequest.grant_url == grant_url).first()

def get_access_tokens_request(db: Session, skip: int = 0, limit: int = 5000):
    return db.query(models.AccessTokenRequest).offset(skip).limit(limit).all()

def get_access_tokens(db: Session, skip: int = 0, limit: int = 5000):
    return db.query(models.AccessToken).offset(skip).limit(limit).all()

def validate_token_format(token: str): #completar
    #print(token)
    if token == None:
        return False
    #print(len(token))
    if len(token) < 30:
        return False
    return True

def validate_user_token(db: Session, token: str, user_id:str):
    if validate_token_format(token):
        user = get_user(db, user_id)
        token_model = get_token(db, token)
        print(type(token_model))
        if token_model != None:
            if user != None and token_model.user_id == user.id:
                return {"status": 200, "error":""}
            else:
                #print("acá estoy")
                return {"status": 403, "error":"you don't have access to this resource"}
        else:
            #print("aca estoy 2")
            return {"status": 401, "error":"invalid token"}
    else:
        #print("aca estoy 3")
        return {"status": 401, "error":"invalid token"}

def validate_token_scope(db: Session, token: str, user_id:str, scope: str):
    if validate_token_format(token):
        user = get_user(db, user_id)
        token_model = get_token(db, token)
        if token_model != None:  #Recibimos un token de usuario
            if user == None or token_model.user_id != user.id:
                return {"status": 403, "error":"you don't have access to this resource"}
        
        access_token = get_access_token(db, token)
        scope_list = scope.split(",")
        if access_token != None:
            print(access_token.scope)
            access_token_scope = access_token.scope.split(",")
            if user != None and access_token.user_id == user.id:
                for scope in scope_list:
                    if scope not in access_token_scope:
                       return {"status": 403, "error":"you don't have access to this resource"}
                return {"status": 200, "error": ""} 
            else:
                return {"status": 403, "error":"you don't have access to this resource"}        
        else: 
            return {"status": 401, "error":"invalid token"}


def create_user_token(db: Session, user_id :str):
    characters = string.ascii_letters + string.digits
    id= ''.join(random.choice(string.digits) for i in range(10))
    token = ''.join(random.choice(characters) for i in range(30))
    db_token = models.UserToken(id = id, token = token, user_id = user_id, validez = True)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return token

def create_user(db: Session, user: schemas.UserBase):
    characters = string.ascii_letters + string.digits
    id= ''.join(random.choice(string.digits) for i in range(10))
    db_user = models.User(id = id, password = user.password, username=user.username, name=user.name, age= user.age, psu_score=user.psu_score,
    university=user.university, gpa_score=user.gpa_score,job=user.job,salary=user.salary,promotion=user.promotion,
    hospital=user.hospital,operations=user.operations, medical_debt=user.medical_debt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_user_token(db, id)
    
    try:
        return {"id": id, "token": token}
    except ValidationError as e:
        print(e.json())

def delete_user(db: Session, user_id: str, token: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db_token = get_token(db, token)
    db.delete(db_token)
    access_token = db.query(models.AccessToken).filter(models.AccessToken.user_id == user_id).first()
    if access_token != None:
        db.delete(db_token)
    #db.flush()
    db.commit()

def request_authentication(db: Session, user_id: str, scope: str, app_id:str): 
    characters = string.ascii_letters + string.digits
    nonce = ''.join(random.choice(characters) for i in range(20))
    expiration = int(time.time()) + 10  #validez de 10 segundos
    id= ''.join(random.choice(string.digits) for i in range(10))
    grant_url = f"/oauth/grant?user_id={user_id}&scopes={scope}&app_id={app_id}&nonce={nonce}"
    accesstokenrequest = models.AccessTokenRequest(id = id, grant_url = grant_url, nonce = nonce, expiration = expiration)
    db.add(accesstokenrequest)
    db.commit()
    db.refresh(accesstokenrequest)
    #return {"grant_url" : grant_url, "expiration" : expiration}
    return accesstokenrequest

def grant_authentication(db: Session, user_id: str, scope: str):
    characters = string.ascii_letters + string.digits
    access_token = ''.join(random.choice(characters) for i in range(30))
    expiration = int(time.time()) + 60  #validez de 60 segundos
    id= ''.join(random.choice(string.digits) for i in range(10))
    accesstoken = models.AccessToken(id = id, token = access_token, expiration = expiration, user_id = user_id, scope = scope)
    db.add(accesstoken)
    db.commit()
    db.refresh(accesstoken)
    return accesstoken
    #return {"access_token" :access_token, "expiration" : expiration}
    

def reset(db: Session):
    users = get_users(db)
    for user in users:
        user_model = get_user(db, user.id)
        db.delete(user_model)
        db.commit()
        #delete_user(db, user.id)
    requests = get_access_tokens_request(db)
    if requests != []:
        for i in requests:
            request = get_access_token_request(db, i.grant_url)
            #print(request)
            db.delete(request)
            db.commit()
    access_tokens = get_access_tokens(db)
    if access_tokens != []:
        for i in access_tokens:
            access_token = get_access_token(db, i.token)
            db.delete(access_token)
            db.commit()
       
 