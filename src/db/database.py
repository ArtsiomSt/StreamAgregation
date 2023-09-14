from db.config import DataBaseConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_settings = DataBaseConfig()

db_url = f"postgresql://{db_settings.pg_user}:{db_settings.pg_password}@{db_settings.pg_host}:{db_settings.pg_port}/{db_settings.db_name}"

engine = create_engine(db_url, echo=True)

SessionMake = sessionmaker(autoflush=False, expire_on_commit=True, bind=engine)
