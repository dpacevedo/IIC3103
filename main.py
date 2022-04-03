from fastapi import FastAPI, HTTPException, Response, status, Depends, Query, Header,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json,requests
from typing import List
from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi.responses import JSONResponse
import crud, models,schemas
import contextlib
from sqlalchemy import MetaData
from database import SessionLocal, engine, Base
from typing import Optional
import time
#Basado en https://fastapi.tiangolo.com/tutorial/sql-databases/ 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    response={"error": 'invalid attributes'}
    return JSONResponse(response, status_code=400)

#methods
@app.post('/token')
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    pass
    #return { 'access_token': form_data.username + 'token', 'token_type': 'bearer'}

@app.get('/oauth/request', status_code = 202) #/oauth/request?user_id=123&scopes=basic,work&app_id=spotify
def request_authentication(user_id: str, scopes: str,  app_id: str, db: Session = Depends(get_db)): 
    scopes_list = scopes.split(",")
    print(scopes_list)    
    for i in scopes_list:
        if i not in ['basic', 'medical', 'work', 'education']:
            raise HTTPException(status_code=400, detail={"error": "please provide a valid scope: basic,education,work,medical"})

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail={"error": "user not found"})

    accesstokenrequest = crud.request_authentication(db, user_id, scopes, app_id)
    #response = crud.request_authentication(db, user_id, scopes, app_id)
    #return {'message' : f"{app_id} está intentado acceder a {scopes}, ¿desea continuar?", "grant_url": response["grant_url"], "expiration": response["expiration"]} 
    return {'message' : f"{app_id} está intentado acceder a {scopes}, ¿desea continuar?", "grant_url": accesstokenrequest.grant_url, "expiration": accesstokenrequest.expiration} 

@app.get('/oauth/grant') #/oauth/request?user_id=123&scopes=basic,education&app_id=snapchat
def grant_authentication(user_id: str, scopes: str,  app_id: str, nonce:str,  Authorization: str = Header(None), db: Session = Depends(get_db)):
    scopes_list = scopes.split(",")    
    for i in scopes_list:
        if i not in ['basic', 'medical', 'work', 'education']:
            raise HTTPException(status_code=400, detail={"error": "please provide a valid scope: basic,education,work,medical"})
    token = Authorization
    #print(token)
    #print(Authorization)
    response = crud.validate_user_token(db, token, user_id)
    if response["status"] == 200:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail={"error": "user not found"})
        
        grant_url = f"/oauth/grant?user_id={user_id}&scopes={scopes}&app_id={app_id}&nonce={nonce}"
        accesstokenrequest = crud.get_access_token_request(db, grant_url)

        if accesstokenrequest is None:
            raise HTTPException(status_code=406, detail={"error": "invalid authorization grant"})
        elif int(time.time()) > accesstokenrequest.expiration: 
            raise HTTPException(status_code=406, detail={"error": "request expired"})
        elif nonce != accesstokenrequest.nonce:
            raise HTTPException(status_code=406, detail={"error": "invalid nonce"})

        #accesstoken = crud.grant_authentication()
        #return {"access_token" : accesstoken["access_token"], "expiration": accesstoken["expiration"]}
        accesstoken = crud.grant_authentication(db, user_id, scopes)
        return {"access_token" : accesstoken.token, "expiration": accesstoken.expiration}

    elif response["status"] == 401:
        raise HTTPException(status_code=401, detail=response["error"])
    else:
        raise HTTPException(status_code=403, detail=response["error"])

@app.get('/')
def home_page():
    #response = crud.get_tokens(db)
    #return response
    return  {'Message': 'Successfuly loaded the home page'}

#Crear usuario
@app.post('/users', status_code = 201)
def create_user(user: schemas.UserBase,  db: Session = Depends(get_db)):
    db_user_search = crud.get_user_by_username(db, username = user.username) 
    if db_user_search: #409 Conflict
        raise HTTPException(status_code=409, detail={"error": 'user already exists'})
    '''
    else:
        print(isinstance(user.username, str))
        print(type(user.username))
        print(user.username)        
        if isinstance(user.username, str) == False or isinstance(user.university, str) == False: 
            raise HTTPException(status_code=400, detail={"error": 'invalid attributes'})
    '''    
    try:
        data_set = crud.create_user(db, user)
        #data_set = {"id": db_user.id, "token": db_user.token} 
        return data_set
    except ValidationError:
        raise HTTPException(status_code=400, detail={"error": 'invalid attributes'})

#Obtener usuario
@app.get('/users/{user_id}', response_model=schemas.User) #/users/?user_id=USER_ID
def request_page(user_id: str, Authorization: str = Header(None), db: Session = Depends(get_db)):
    token = Authorization
    response = crud.validate_user_token(db, token, user_id)
    if response["status"] == 200:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return db_user
    elif response["status"] == 403:
        raise HTTPException(status_code=403, detail=response["error"])
    else:
        raise HTTPException(status_code=401, detail=response["error"])

#Editar usuario (https://sqlmodel.tiangolo.com/tutorial/fastapi/update/)
@app.patch('/users/{user_id}', response_model=schemas.User) #/users/?user_id=USER_ID
def edit_page(user: schemas.UserUpdate, user_id: str, Authorization: str = Header(None), db: Session = Depends(get_db)):
    token = Authorization
    response = crud.validate_user_token(db, token, user_id)
    if response["status"] == 200:    
        db_user = crud.get_user(db, user_id=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="user not found")

        user_data = user.dict(exclude_unset=True)

        db_user_search = crud.get_user_by_username(db, user.username)
        if db_user_search: #409 Conflict
            raise HTTPException(status_code=409, detail={'error': 'username is taken'})
        try:                 
            #for key, value in user_data.items():
                #setattr(db_user, key, value)
            #return {"mensaje" : "informacion recibida, no actualizada aún"}
            #db.add(db_user)
            #db.commit()
            #db.refresh(db_user)
            #db_user.update(user_data, synchronize_session = False)
            if user.username != None:
                db_user.username = user.username
            if user.age != None:
                db_user.age = user.age
            if user.job != None:
                db_user.job = user.job
            if user.salary != None:
                db_user.salary = user.salary
            if user.promotion != None:
                db_user.promotion = user.promotion
            if user.hospital != None:
                db_user.hospital = user.hospital
            if user.username != None:
                db_user.medical_debt = user.medical_debt
            if user.psu_score != None:
                db_user.psu_score = user.psu_score
            #db.save(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except ValidationError:
            raise HTTPException(status_code=400, detail={"error": 'invalid attributes'})
    elif response["status"] == 403:
        raise HTTPException(status_code=403, detail=response["error"])
    else:
        raise HTTPException(status_code=401, detail=response["error"])   


#Eliminar usuario
@app.delete('/users/{user_id}', status_code = 204, response_class=Response) #/users/?user_id=USER_ID 
def delete_page(user_id: str, Authorization: str = Header(None), db: Session = Depends(get_db) ):
    token = Authorization 
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=401, detail="user not found")
    else:
        response = crud.validate_user_token(db, token, user_id)
        if response["status"] == 200:
            crud.delete_user(db, user_id, token)
            return None
        elif response["status"] == 403:
            raise HTTPException(status_code=403, detail=response["error"])
        else:
            raise HTTPException(status_code=401, detail=response["error"])

 

#Scope, retorna los datos del usuario del scope dado
@app.get('/users/{user_id}/{scope}')  #/users/?user_id=USER_ID/scope=SCOPE
def scope_page(user_id: str, scope: str, Authorization: str = Header(None), db: Session = Depends(get_db) ):
    token = Authorization 
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        response = crud.validate_token_scope(db, token, user_id, scope)
        if response["status"] == 200:
            if scope == 'basic':
                data_set = {'id': db_user.id, 'username': db_user.username , 'name': db_user.name, 'age': db_user.age} 
                return data_set

            elif scope == 'education':
                data_set = {'id': db_user.id, 'psu_score' : db_user.psu_score, 'university': db_user.university, 'gpa_score': db_user.gpa_score} 
                return data_set

            elif scope == 'work':
                data_set = { 'id': db_user.id, 'job': db_user.job , 'salary': db_user.salary, 'promotion': db_user.promotion} 
                return data_set

            elif scope == 'medical':
                data_set = {'id': db_user.id, 'hospital': db_user.hospital, 'operations': db_user.operations, 'medical_debt': db_user.medical_debt} 
                return data_set
        elif response["status"] == 403:
            raise HTTPException(status_code=403, detail=response["error"])
        else:
            raise HTTPException(status_code=401, detail=response["error"])

'''
meta = MetaData()
#Resetear la base de datos, basado en: https://stackoverflow.com/questions/4763472/sqlalchemy-clear-database-content-but-dont-drop-the-schema
@app.get('/reset')
def reset():    
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()
'''
#Basado en https://stackoverflow.com/questions/16573802/flask-sqlalchemy-how-to-delete-all-rows-in-a-single-table 
@app.get('/reset')
def reset(db: Session = Depends(get_db) ):
    crud.reset(db)
    '''
    try:
        num_rows_deleted = db.query(models.User).delete()
        num_rows_deleted_token = db.query(models.UserToken).delete()
        db.commit()
    except:
        db.rollback()
        '''