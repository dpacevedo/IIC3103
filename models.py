from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

#Basado en https://fastapi.tiangolo.com/tutorial/sql-databases/

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    password = Column(String)
    username = Column(String, unique=True) #requerido
    name = Column(String)  #requerido
    age = Column(Integer) #requerido
    psu_score = Column(Integer)
    university = Column(String)
    gpa_score = Column(Float)
    job = Column(String)
    salary = Column(Float)
    promotion = Column(Boolean)
    hospital = Column(String)
    operations = Column(ARRAY(String))  #Column(ARRAY(String)) 
    medical_debt = Column(Float)

    token = relationship("UserToken", uselist=False, cascade='all, delete-orphan', backref="user") 

class UserToken(Base):
    __tablename__ = "users_tokens"

    id = Column(String, primary_key=True, index=True)
    #user_id = Column(String)
    token = Column(String)
    validez = Column(Boolean)

    user_id = Column(String, ForeignKey("users.id"))
    #user = relationship("User", back_populates="token") 

class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(String, primary_key=True, index=True)
    token = Column(String) 
    expiration = Column(Integer)
    scope = Column(String)
    user_id = Column(String) 

class AccessTokenRequest(Base):
    __tablename__ = "access_tokens_request"

    id = Column(String, primary_key=True, index=True)
    grant_url = Column(String)
    nonce = Column(String)
    expiration = Column(Integer)
    
