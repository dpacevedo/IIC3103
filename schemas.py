from typing import List, Optional

from pydantic import BaseModel, validator, StrictStr, StrictInt, StrictFloat

#Basado en https://fastapi.tiangolo.com/tutorial/sql-databases/
def type_function(value):
    get_type = lambda value: str(type(value)).split("'")[1]
    return get_type

class UserBase(BaseModel):
    username: StrictStr
    name: StrictStr
    age : StrictInt
    password: StrictStr
    psu_score: Optional[StrictInt] = None
    university: Optional[StrictStr] = None
    gpa_score: Optional[StrictFloat] = None
    job: Optional[StrictStr] = None
    salary: Optional[StrictFloat] = None
    promotion: Optional[bool] = None
    hospital: Optional[StrictStr] = None
    operations: Optional[List[StrictStr]] = None
    medical_debt: Optional[StrictFloat] = None

    class Config:
        orm_mode = True
    '''
    @validator('username')
    def username_validator(cls, value):
        print(isinstance(value,str))
        if value != None and isinstance(value, str) == False:
            raise ValueError("Invalid username")

    @validator("name")
    def name_validator(cls, value):
        type = type_function(value)
        if type != 'str':
            raise ValueError("Invalid name")

    @validator("password")
    def password_validator(cls, value):
        type = type_function(value)
        if type != 'str':
            raise ValueError("Invalid password")

    @validator("age")
    def age_validator(cls, value):
        type = type_function(value)
        if type != 'int':
            raise ValueError("Invalid age")

    @validator("psu_score")
    def psu_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'int':
            raise ValueError("Invalid psu_score")

    @validator("university")
    def university_validator(cls, value):
        type = type_function(value)
        if value != None and isinstance(value, str) == False:
            raise ValueError("Invalid university")

    @validator("gpa_score")
    def gpa_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError("Invalid gpa_score")
    
    @validator("salary")
    def salary_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError("Invalid salary")
    
    @validator("job")
    def job_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError("Invalid job")
    
    @validator("promotion")
    def promotion_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'bool':
            raise ValueError("Invalid promotion")

    @validator("hospital")
    def hospital_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError("Invalid hospital")
    
    @validator("medical_debt")
    def medical_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError("Invalid medical debt")
 '''
class UserUpdate(BaseModel):
    username: Optional[StrictStr] = None
    #name: Optional[StrictStr] = None
    age : Optional[StrictInt] = None
    #password: Optional[StrictStr] = None
    psu_score: Optional[StrictInt] = None
    #university: Optional[StrictStr] = None
    #gpa_score: Optional[StrictFloat] = None
    job: Optional[StrictStr] = None
    salary: Optional[StrictFloat] = None
    promotion: Optional[bool] = None
    hospital: Optional[StrictStr] = None
    #operations: Optional[List[StrictStr]] = None
    medical_debt: Optional[StrictFloat] = None

    class Config:
        orm_mode = True
    '''   
    @validator("username")
    def username_validator(cls, value):
        type = type_function(value)
        print(type)
        #if value != None and type != 'str':
            #raise ValueError("Invalid username")

    @validator("name")
    def name_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError()

    @validator("password")
    def password_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError()

    @validator("age")
    def age_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'int':
            raise ValueError()

    @validator("psu_score")
    def psu_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'int':
            raise ValueError()
    
    @validator("university")
    def university_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError("Invalid university")

    @validator("gpa_score")
    def gpa_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError()
    
    @validator("salary")
    def salary_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError()
    
    @validator("job")
    def job_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError()
    
    @validator("promotion")
    def promotion_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'bool':
            raise ValueError()

    @validator("hospital")
    def hospital_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'str':
            raise ValueError()
    
    @validator("medical_debt")
    def medical_validator(cls, value):
        type = type_function(value)
        if value != None and type != 'float':
            raise ValueError()

 '''
class User(UserBase):
    id: str

    class Config:
        orm_mode = True

#____________________________________________-
class UserToken(BaseModel):
    id: str
    token: str
    user_id: str
    validez: bool

    class Config:
        orm_mode = True
    
#____________________________________________-
class AccessToken(BaseModel):
    id: str
    token: str
    expiration : int
    user_id: str
    scope: str
    class Config:
        orm_mode = True

#____________________________________________-
 
class AccessTokenRequest(BaseModel):
    id: int
    grant_url: str
    nonce : str
    expiration : int

    class Config:
        orm_mode = True