from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.base import Base  # noqa
from app.models.document import *  # noqa

from app.settings import get_settings

settings = get_settings()

async_engine = create_async_engine(settings.async_database_url)

AsyncSessionLocal = async_sessionmaker(autoflush=False, bind=async_engine)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
