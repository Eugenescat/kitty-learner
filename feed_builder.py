"""Assemble posts into a feed and render to HTML."""

import os
import random
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from generator import Post


def select_posts_random(posts: list[Post], count: int = None, ratio: float = 0.5) -> list[Post]:
    """
    Randomly select a subset of posts for the feed.
    
    Args:
        posts: All generated posts
        count: Exact number of posts to select (overrides ratio)
        ratio: Fraction of posts to include (default: 50%)
    
    Returns:
        Selected posts in random order
    """
    if count is None:
        count = max(1, int(len(posts) * ratio))
    
    count = min(count, len(posts))
    selected = random.sample(posts, count)
    random.shuffle(selected)
    
    return selected


def select_posts_by_controversy(posts: list[Post], count: int = None) -> list[Post]:
    """
    Select posts prioritizing high controversy topics.
    (For future use - more engaging feed)
    """
    controversy_order = {"high": 0, "medium": 1, "low": 2}
    sorted_posts = sorted(posts, key=lambda p: controversy_order.get(p.topic.controversy_level, 2))
    
    if count:
        sorted_posts = sorted_posts[:count]
    
    # Add some randomness
    random.shuffle(sorted_posts)
    return sorted_posts


def select_posts_by_difficulty(posts: list[Post], ascending: bool = True) -> list[Post]:
    """
    Order posts by difficulty (easy to hard or vice versa).
    Good for learning progression.
    """
    return sorted(posts, key=lambda p: p.topic.difficulty, reverse=not ascending)


def render_feed(posts: list[Post], output_path: str, paper_title: str = "Paper Feed", paper_summary: str = "") -> str:
    """
    Render posts to an HTML file.
    
    Returns the path to the generated HTML file.
    """
    # Setup Jinja2
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("feed.html")
    
    # Render
    html = template.render(
        posts=posts,
        paper_title=paper_title,
        paper_summary=paper_summary,
    )
    
    # Write to file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / output_path
    output_file.write_text(html, encoding="utf-8")
    
    return str(output_file.absolute())


def build_feed(
    posts: list[Post],
    paper_title: str,
    paper_summary: str = "",
    output_filename: str = "feed.html",
    selection_mode: str = "random",
    post_count: int = None,
    post_ratio: float = 0.5,
) -> str:
    """
    Main entry point: select posts and render to HTML.
    
    Args:
        posts: All generated posts
        paper_title: Title for the feed
        paper_summary: One-line summary of the paper
        output_filename: Name of output HTML file
        selection_mode: "random", "controversy", "difficulty", or "all"
        post_count: Exact number of posts (overrides ratio)
        post_ratio: Fraction of posts to include (default: 50%)
    
    Returns:
        Path to the generated HTML file
    """
    # Select posts based on mode
    if selection_mode == "all":
        selected_posts = posts.copy()
        random.shuffle(selected_posts)
    elif selection_mode == "controversy":
        selected_posts = select_posts_by_controversy(posts, post_count)
    elif selection_mode == "difficulty":
        selected_posts = select_posts_by_difficulty(posts)
        if post_count:
            selected_posts = selected_posts[:post_count]
    else:  # random (default)
        selected_posts = select_posts_random(posts, post_count, post_ratio)
    
    print(f"📱 Selected {len(selected_posts)} posts for feed (mode: {selection_mode})")
    
    # Render
    output_path = render_feed(selected_posts, output_filename, paper_title, paper_summary)
    
    return output_path
