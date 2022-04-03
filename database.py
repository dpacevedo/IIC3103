from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import psycopg2

SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_URL']

#conn = psycopg2.connect(DATABASE_URL, sslmode='require')


#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
#SQLALCHEMY_DATABASE_URL = "postgres://jnwsttwrjkynls:b1e71a581cd266a6367022fddb7edea0e7e121f0917e8c5f3fe65636da4e3cc0@ec2-18-214-134-226.compute-1.amazonaws.com:5432/dbp5n54tuj4v14"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
