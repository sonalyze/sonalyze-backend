from sqlmodel import Session, create_engine
from dotenv import dotenv_values

connection_string = dotenv_values(".env")["DB_CONNECTION_STRING"] or ""
engine = create_engine(
    connection_string
    )
    

def get_session():
    with Session(engine) as session:
        yield session