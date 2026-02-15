"""PostgreSQL database storage for topics and posts."""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle Railway's postgres:// vs postgresql:// URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None
Base = declarative_base()


class Feed(Base):
    """Stores complete feed data (topics + posts)."""
    __tablename__ = "feeds"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(50), unique=True, index=True)
    title = Column(String(500))
    summary = Column(Text)
    topics_json = Column(JSON)  # Stores topics array
    posts_json = Column(JSON)   # Stores posts array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database tables."""
    if engine:
        Base.metadata.create_all(engine)
        print("✅ Database tables created")
    else:
        print("⚠️ No DATABASE_URL found, using memory storage")


def get_session():
    """Get a database session."""
    if SessionLocal:
        return SessionLocal()
    return None


# ============ Storage Functions ============

def save_feed(file_id: str, title: str, summary: str, topics_data: dict, posts_data: list) -> bool:
    """Save complete feed to database."""
    session = get_session()
    if not session:
        print("⚠️ Database not available")
        return False
    
    try:
        # Check if feed exists
        existing = session.query(Feed).filter_by(file_id=file_id).first()
        
        if existing:
            # Update existing
            existing.title = title
            existing.summary = summary
            existing.topics_json = topics_data
            existing.posts_json = posts_data
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            feed = Feed(
                file_id=file_id,
                title=title,
                summary=summary,
                topics_json=topics_data,
                posts_json=posts_data,
            )
            session.add(feed)
        
        session.commit()
        print(f"💾 Feed saved to database: {file_id}")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def load_feed(file_id: str) -> dict | None:
    """Load feed from database."""
    session = get_session()
    if not session:
        return None
    
    try:
        feed = session.query(Feed).filter_by(file_id=file_id).first()
        if not feed:
            return None
        
        return {
            "file_id": feed.file_id,
            "title": feed.title,
            "summary": feed.summary,
            "topics": feed.topics_json,
            "posts": feed.posts_json,
            "created_at": feed.created_at.isoformat() if feed.created_at else None,
        }
    finally:
        session.close()


def list_all_feeds() -> list[dict]:
    """List all saved feeds."""
    session = get_session()
    if not session:
        return []
    
    try:
        feeds = session.query(Feed).order_by(Feed.created_at.desc()).all()
        return [
            {
                "file_id": f.file_id,
                "title": f.title,
                "summary": f.summary,
                "post_count": len(f.posts_json) if f.posts_json else 0,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in feeds
        ]
    finally:
        session.close()


def delete_feed(file_id: str) -> bool:
    """Delete a feed from database."""
    session = get_session()
    if not session:
        return False
    
    try:
        feed = session.query(Feed).filter_by(file_id=file_id).first()
        if feed:
            session.delete(feed)
            session.commit()
            print(f"🗑️ Feed deleted: {file_id}")
            return True
        return False
    except Exception as e:
        print(f"❌ Delete error: {e}")
        session.rollback()
        return False
    finally:
        session.close()


# ============ Fallback to JSON (for local dev without DB) ============

import storage as json_storage

def save_feed_with_fallback(file_id: str, title: str, summary: str, topics_data: dict, posts_data: list):
    """Save to database, fallback to JSON if no DB."""
    if DATABASE_URL:
        save_feed(file_id, title, summary, topics_data, posts_data)
    else:
        # Fallback to JSON storage
        feed_data = {
            "title": title,
            "summary": summary,
            "topics": topics_data,
            "posts": posts_data,
        }
        json_storage.save_feed(file_id, feed_data)


def load_feed_with_fallback(file_id: str) -> dict | None:
    """Load from database, fallback to JSON if no DB."""
    if DATABASE_URL:
        return load_feed(file_id)
    else:
        return json_storage.load_feed(file_id)


def list_feeds_with_fallback() -> list[dict]:
    """List from database, fallback to JSON if no DB."""
    if DATABASE_URL:
        return list_all_feeds()
    else:
        return json_storage.list_all_feeds()
