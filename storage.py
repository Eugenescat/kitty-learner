"""Local JSON file storage for topics and posts."""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional


# Storage directory
STORAGE_DIR = Path(__file__).parent / "data"
TOPICS_DIR = STORAGE_DIR / "topics"
POSTS_DIR = STORAGE_DIR / "posts"
FEEDS_DIR = STORAGE_DIR / "feeds"


def init_storage():
    """Initialize storage directories."""
    STORAGE_DIR.mkdir(exist_ok=True)
    TOPICS_DIR.mkdir(exist_ok=True)
    POSTS_DIR.mkdir(exist_ok=True)
    FEEDS_DIR.mkdir(exist_ok=True)


def save_topics(file_id: str, title: str, topics_data: dict) -> str:
    """
    Save extracted topics to JSON file.
    
    Args:
        file_id: Unique identifier for the upload
        title: Paper title
        topics_data: Topics dict from topic_extractor
        
    Returns:
        Path to saved file
    """
    init_storage()
    
    data = {
        "file_id": file_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "paper_summary": topics_data.get("paper_summary", ""),
        "topics": topics_data.get("topics", []),
        "recommended_order": topics_data.get("recommended_order", []),
    }
    
    filepath = TOPICS_DIR / f"{file_id}_topics.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Topics saved to: {filepath}")
    return str(filepath)


def load_topics(file_id: str) -> Optional[dict]:
    """Load topics from JSON file."""
    filepath = TOPICS_DIR / f"{file_id}_topics.json"
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(file_id: str, title: str, posts_data: list[dict]) -> str:
    """
    Save generated posts to JSON file.
    
    Args:
        file_id: Unique identifier for the upload
        title: Paper title
        posts_data: List of post dicts
        
    Returns:
        Path to saved file
    """
    init_storage()
    
    data = {
        "file_id": file_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "post_count": len(posts_data),
        "posts": posts_data,
    }
    
    filepath = POSTS_DIR / f"{file_id}_posts.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Posts saved to: {filepath}")
    return str(filepath)


def load_posts(file_id: str) -> Optional[dict]:
    """Load posts from JSON file."""
    filepath = POSTS_DIR / f"{file_id}_posts.json"
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_feed(file_id: str, feed_data: dict) -> str:
    """
    Save complete feed (topics + posts combined) to JSON file.
    
    Args:
        file_id: Unique identifier
        feed_data: Complete feed dict with title, summary, posts
        
    Returns:
        Path to saved file
    """
    init_storage()
    
    data = {
        **feed_data,
        "file_id": file_id,
        "created_at": datetime.now().isoformat(),
    }
    
    filepath = FEEDS_DIR / f"{file_id}_feed.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Feed saved to: {filepath}")
    return str(filepath)


def load_feed(file_id: str) -> Optional[dict]:
    """Load feed from JSON file."""
    filepath = FEEDS_DIR / f"{file_id}_feed.json"
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_all_feeds() -> list[dict]:
    """List all saved feeds with metadata."""
    init_storage()
    
    feeds = []
    for filepath in FEEDS_DIR.glob("*_feed.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                feeds.append({
                    "file_id": data.get("file_id", filepath.stem.replace("_feed", "")),
                    "title": data.get("title", "Untitled"),
                    "summary": data.get("summary", ""),
                    "post_count": len(data.get("posts", [])),
                    "created_at": data.get("created_at", ""),
                })
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    # Sort by creation time (newest first)
    feeds.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return feeds


def delete_feed(file_id: str) -> bool:
    """Delete all data for a feed."""
    deleted = False
    
    for dir_path in [TOPICS_DIR, POSTS_DIR, FEEDS_DIR]:
        for pattern in [f"{file_id}_*.json"]:
            for filepath in dir_path.glob(pattern):
                filepath.unlink()
                deleted = True
                print(f"🗑️ Deleted: {filepath}")
    
    return deleted
