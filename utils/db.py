from sqlalchemy import create_engine

def get_connection():
    return create_engine(
        "mysql+pymysql://root:fast@localhost:3306/petrol_db"
    )