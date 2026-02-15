"""LLM-based content generation for posts and replies."""

import os
import random
from dataclasses import dataclass
from anthropic import Anthropic
from dotenv import load_dotenv

from agents import Agent, get_all_agents, get_reply_prompt
from topic_extractor import Topic, PaperTopics


load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class Reply:
    """A reply to a post."""
    agent: Agent
    content: str
    likes: int


@dataclass
class Post:
    """A post in the feed."""
    id: int
    agent: Agent
    topic: Topic
    content: str
    likes: int
    replies: list[Reply]


def generate_post_for_topic(agent: Agent, topic: Topic, paper_summary: str) -> str:
    """Generate a post from an agent about a specific topic."""
    
    topic_context = f"""论文概述：{paper_summary}

本次讨论的知识点：
- 标题：{topic.title}
- 核心内容：{topic.core_idea}
- 为什么重要：{topic.why_it_matters}
- 争议程度：{topic.controversy_level}
- 来源章节：{topic.source_section}
- 难度：{topic.difficulty}/10"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=agent.system_prompt,
        messages=[
            {"role": "user", "content": f"请根据以下知识点发一条帖子：\n\n{topic_context}"},
        ],
    )
    return response.content[0].text


def generate_reply_for_post(agent: Agent, original_post: str, topic: Topic) -> str:
    """Generate a reply from an agent to a post about a topic."""
    reply_prompt = get_reply_prompt(agent)
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        system=reply_prompt,
        messages=[
            {"role": "user", "content": f"原帖内容：\n{original_post}\n\n（讨论的知识点：{topic.title}）\n\n请写一条评论回复这个帖子："},
        ],
    )
    return response.content[0].text


def generate_all_posts(
    paper_topics: PaperTopics,
    agents_per_topic: int = 3,
    replies_per_post: int = 2
) -> list[Post]:
    """
    Generate posts for all topics from multiple agents.
    
    This creates n_topics * agents_per_topic posts.
    
    Args:
        paper_topics: Extracted topics from the paper
        agents_per_topic: How many agents post about each topic (default: 3)
        replies_per_post: How many replies each post gets (default: 2)
    
    Returns:
        List of all generated posts
    """
    all_agents = get_all_agents()
    all_posts = []
    post_id = 0
    
    for topic in paper_topics.topics:
        # Select random agents for this topic
        posting_agents = random.sample(all_agents, min(agents_per_topic, len(all_agents)))
        
        for agent in posting_agents:
            print(f"Generating post {post_id + 1}: {agent.nickname} on '{topic.title[:20]}...'")
            
            # Generate main post
            post_content = generate_post_for_topic(agent, topic, paper_topics.paper_summary)
            
            # Generate replies from other agents
            other_agents = [a for a in all_agents if a.id != agent.id]
            replying_agents = random.sample(other_agents, min(replies_per_post, len(other_agents)))
            
            replies = []
            for reply_agent in replying_agents:
                print(f"  └─ Reply by {reply_agent.nickname}")
                reply_content = generate_reply_for_post(reply_agent, post_content, topic)
                replies.append(Reply(
                    agent=reply_agent,
                    content=reply_content,
                    likes=random.randint(5, 50),
                ))
            
            all_posts.append(Post(
                id=post_id,
                agent=agent,
                topic=topic,
                content=post_content,
                likes=random.randint(20, 200),
                replies=replies,
            ))
            post_id += 1
    
    print(f"\n✅ Generated {len(all_posts)} posts total")
    return all_posts


# Keep old function for backward compatibility
def generate_feed_for_chunks(chunks: list, posts_per_chunk: int = 1, replies_per_post: int = 2) -> list[Post]:
    """Legacy function: Generate posts from text chunks (old behavior)."""
    all_agents = get_all_agents()
    posts = []
    post_id = 0
    
    for chunk in chunks:
        posting_agent = random.choice(all_agents)
        
        print(f"Generating post {post_id + 1} by {posting_agent.nickname}...")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=posting_agent.system_prompt,
            messages=[
                {"role": "user", "content": f"请根据以下内容发一条帖子：\n\n{chunk.text}"},
            ],
        )
        post_content = response.content[0].text
        
        other_agents = [a for a in all_agents if a.id != posting_agent.id]
        replying_agents = random.sample(other_agents, min(replies_per_post, len(other_agents)))
        
        replies = []
        for reply_agent in replying_agents:
            print(f"  Generating reply by {reply_agent.nickname}...")
            reply_prompt = get_reply_prompt(reply_agent)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=reply_prompt,
                messages=[
                    {"role": "user", "content": f"原帖内容：\n{post_content}\n\n请写一条评论回复这个帖子："},
                ],
            )
            replies.append(Reply(
                agent=reply_agent,
                content=response.content[0].text,
                likes=random.randint(5, 50),
            ))
        
        # Create a dummy topic for legacy posts
        dummy_topic = Topic(
            topic_id=post_id,
            title="",
            core_idea=chunk.text[:200],
            why_it_matters="",
            controversy_level="low",
            source_section="",
            difficulty=5,
        )
        
        posts.append(Post(
            id=post_id,
            agent=posting_agent,
            topic=dummy_topic,
            content=post_content,
            likes=random.randint(20, 200),
            replies=replies,
        ))
        post_id += 1
    
    return posts


if __name__ == "__main__":
    # Quick test
    from topic_extractor import load_topics_json
    import sys
    
    if len(sys.argv) > 1:
        topics = load_topics_json(sys.argv[1])
        posts = generate_all_posts(topics, agents_per_topic=2, replies_per_post=1)
        
        print("\n--- Sample Post ---")
        if posts:
            p = posts[0]
            print(f"Topic: {p.topic.title}")
            print(f"By: {p.agent.nickname}")
            print(f"Content: {p.content[:200]}...")
