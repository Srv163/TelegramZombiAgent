from sqlalchemy import (
    BigInteger, Column, Integer, String, Text, JSON, TIMESTAMP, Boolean, Float, ForeignKey, text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from .config import settings

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    title = Column(String)
    enabled = Column(Boolean, default=True)
    style_profile = Column(JSON, server_default=text("'{}'::jsonb"))

class PostRaw(Base):
    __tablename__ = "posts_raw"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    tg_post_id = Column(BigInteger, nullable=False)
    message = Column(Text)
    media = Column(JSON)
    posted_at = Column(TIMESTAMP(timezone=True))
    __table_args__ = (text("UNIQUE (source_id, tg_post_id)"),)

    source = relationship("Source")

class PostZombie(Base):
    __tablename__ = "posts_zombified"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    raw_id = Column(BigInteger, ForeignKey("posts_raw.id"))
    zombie_text = Column(Text)
    zombie_media = Column(JSON)
    zombie_level = Column(Integer, server_default=text("2"))
    safety_flags = Column(JSON, server_default=text("'{}'::jsonb"))
    similarity_score = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    raw = relationship("PostRaw")

class PublishQueue(Base):
    __tablename__ = "publish_queue"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    zombie_id = Column(BigInteger, ForeignKey("posts_zombified.id"))
    scheduled_at = Column(TIMESTAMP(timezone=True))
    status = Column(String, server_default=text("'queued'"))
    result_msg_id = Column(BigInteger)

    zombie = relationship("PostZombie")

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)