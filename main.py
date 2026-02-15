#!/usr/bin/env python3
"""
Passive Learner - Transform PDFs into scrollable social-media-style feeds.

New Architecture:
1. Extract topics from paper (Claude analyzes and creates structured JSON)
2. Generate posts for each topic from multiple agents (n topics × m agents)
3. Select subset of posts and build feed (random or other algorithms)

Usage:
    python main.py <pdf_file> [options]
    python main.py --from-topics <topics.json> [options]
"""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

from pdf_parser import extract_text_from_pdf
from topic_extractor import extract_topics, save_topics_json, load_topics_json
from generator import generate_all_posts
from feed_builder import build_feed


def main():
    parser = argparse.ArgumentParser(
        description="Transform a PDF into a RedNote-style learning feed"
    )
    
    # Input options
    parser.add_argument("pdf_file", nargs="?", help="Path to the PDF file to process")
    parser.add_argument(
        "--from-topics", "-f",
        help="Load topics from existing JSON file (skip extraction step)"
    )
    
    # Output options
    parser.add_argument(
        "--title", "-t",
        default=None,
        help="Title for the feed (defaults to filename)"
    )
    parser.add_argument(
        "--save-topics", "-s",
        help="Save extracted topics to JSON file for reuse"
    )
    
    # Generation options
    parser.add_argument(
        "--agents-per-topic", "-a",
        type=int,
        default=3,
        help="Number of agents to post about each topic (default: 3)"
    )
    parser.add_argument(
        "--replies-per-post", "-r",
        type=int,
        default=2,
        help="Number of replies per post (default: 2)"
    )
    
    # Feed selection options
    parser.add_argument(
        "--selection", "-m",
        choices=["random", "controversy", "difficulty", "all"],
        default="random",
        help="Post selection mode (default: random)"
    )
    parser.add_argument(
        "--post-count", "-n",
        type=int,
        default=None,
        help="Exact number of posts to include in feed"
    )
    parser.add_argument(
        "--post-ratio",
        type=float,
        default=0.5,
        help="Fraction of posts to include (default: 0.5)"
    )
    
    # Other options
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't automatically open the feed in browser"
    )
    parser.add_argument(
        "--topics-only",
        action="store_true",
        help="Only extract topics, don't generate posts"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.pdf_file and not args.from_topics:
        parser.error("Either pdf_file or --from-topics is required")
    
    # Step 1: Get topics (either extract or load)
    if args.from_topics:
        print(f"📂 Loading topics from: {args.from_topics}")
        paper_topics = load_topics_json(args.from_topics)
        title = args.title or Path(args.from_topics).stem
    else:
        pdf_path = Path(args.pdf_file)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_path}")
            sys.exit(1)
        if not pdf_path.suffix.lower() == ".pdf":
            print(f"❌ Error: Not a PDF file: {pdf_path}")
            sys.exit(1)
        
        title = args.title or pdf_path.stem
        
        print(f"📄 Processing: {pdf_path.name}")
        print(f"📝 Title: {title}")
        print()
        
        # Extract text
        print("🔍 Extracting text from PDF...")
        paper_text = extract_text_from_pdf(str(pdf_path))
        print(f"   Extracted {len(paper_text)} characters")
        print()
        
        # Extract topics
        paper_topics = extract_topics(paper_text)
        
        # Optionally save topics
        if args.save_topics:
            save_topics_json(paper_topics, args.save_topics)
    
    # Show extracted topics
    print(f"\n📋 Paper Summary: {paper_topics.paper_summary}")
    print(f"\n📚 Extracted {len(paper_topics.topics)} topics:")
    for t in paper_topics.topics:
        controversy_emoji = {"high": "🔥", "medium": "💬", "low": "📖"}.get(t.controversy_level, "")
        print(f"   {t.topic_id}. {t.title} {controversy_emoji} (difficulty: {t.difficulty}/10)")
    print(f"\n📖 Recommended order: {paper_topics.recommended_order}")
    print()
    
    # Stop here if topics-only mode
    if args.topics_only:
        print("✅ Topics extracted. Use --from-topics to generate posts later.")
        return
    
    # Step 2: Generate posts
    print("🤖 Generating posts from agents...")
    print(f"   {len(paper_topics.topics)} topics × {args.agents_per_topic} agents = {len(paper_topics.topics) * args.agents_per_topic} posts")
    print(f"   Each post gets {args.replies_per_post} replies")
    print()
    
    posts = generate_all_posts(
        paper_topics,
        agents_per_topic=args.agents_per_topic,
        replies_per_post=args.replies_per_post,
    )
    
    # Step 3: Build feed
    print()
    print("🎨 Building feed...")
    
    output_filename = f"{title.replace(' ', '_')}_feed.html"
    output_path = build_feed(
        posts,
        paper_title=title,
        paper_summary=paper_topics.paper_summary,
        output_filename=output_filename,
        selection_mode=args.selection,
        post_count=args.post_count,
        post_ratio=args.post_ratio,
    )
    
    print(f"✅ Feed saved to: {output_path}")
    print()
    
    # Step 4: Open in browser
    if not args.no_open:
        print("🌐 Opening in browser...")
        webbrowser.open(f"file://{output_path}")
    
    print()
    print("🎉 Done! Enjoy your learning feed!")


if __name__ == "__main__":
    main()
