import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

APP_USER = os.getenv('APP_USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
DATABASE = os.getenv('DATABASE')

DATABASE_URL = (
    f"postgresql+psycopg2://{APP_USER}:{PASSWORD}"
    f"@localhost:{PORT}/{DATABASE}"
    )

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit = False, 
                            autoflush= False, 
                            bind=engine)

Base = declarative_base()