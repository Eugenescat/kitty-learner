"""Extract discussion topics from paper using Claude."""

import os
import json
from dataclasses import dataclass
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


SYSTEM_PROMPT = """你是一个专业的学术内容策划师。你的任务是将一篇 CS/AI 论文拆解为 5-10 个适合在社交媒体上讨论的独立知识点。"""

USER_PROMPT_TEMPLATE = """请阅读这篇论文，完成以下任务：

1. **论文一句话概括**：用一句大白话说清楚这篇论文在干什么

2. **拆解为 5-10 个可讨论的知识点**，每个知识点包含：
   - topic_id: 编号
   - title: 一个吸引眼球的标题（小红书风格，口语化，可以带 emoji）
   - core_idea: 2-3 句话说清楚这个知识点的核心
   - why_it_matters: 为什么这个点值得讨论
   - controversy_level: low / medium / high（越高越适合辩论）
   - source_section: 对应论文的哪个章节
   - difficulty: 根据理解难度/抽象程度打分（1-10分，10分最难）

3. **建议讨论顺序**：给出一个推荐的阅读/刷帖顺序，从最容易理解到最深入

请以 JSON 格式输出，格式如下：
```json
{{
  "paper_summary": "一句话概括",
  "topics": [
    {{
      "topic_id": 1,
      "title": "标题",
      "core_idea": "核心内容",
      "why_it_matters": "为什么重要",
      "controversy_level": "low/medium/high",
      "source_section": "章节",
      "difficulty": 5
    }}
  ],
  "recommended_order": [1, 3, 2, 4, 5]
}}
```

以下是论文内容：

---
{paper_content}
---"""


@dataclass
class Topic:
    """A discussion topic extracted from the paper."""
    topic_id: int
    title: str
    core_idea: str
    why_it_matters: str
    controversy_level: str  # low, medium, high
    source_section: str
    difficulty: int


@dataclass
class PaperTopics:
    """All topics extracted from a paper."""
    paper_summary: str
    topics: list[Topic]
    recommended_order: list[int]


def extract_topics(paper_text: str, max_tokens: int = 4000) -> PaperTopics:
    """
    Extract discussion topics from paper text using Claude.
    
    Args:
        paper_text: Full text of the paper
        max_tokens: Max tokens for the response
        
    Returns:
        PaperTopics object with all extracted topics
    """
    # Truncate paper if too long (keep first ~50k chars)
    if len(paper_text) > 50000:
        paper_text = paper_text[:50000] + "\n\n[... 论文内容过长，已截断 ...]"
    
    user_prompt = USER_PROMPT_TEMPLATE.format(paper_content=paper_text)
    
    print("🔍 Analyzing paper and extracting topics...")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )
    
    # Parse JSON from response
    response_text = response.content[0].text
    
    # Extract JSON from markdown code block if present
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    else:
        json_str = response_text.strip()
    
    data = json.loads(json_str)
    
    # Convert to dataclass
    topics = [
        Topic(
            topic_id=t["topic_id"],
            title=t["title"],
            core_idea=t["core_idea"],
            why_it_matters=t["why_it_matters"],
            controversy_level=t["controversy_level"],
            source_section=t["source_section"],
            difficulty=t["difficulty"],
        )
        for t in data["topics"]
    ]
    
    return PaperTopics(
        paper_summary=data["paper_summary"],
        topics=topics,
        recommended_order=data.get("recommended_order", [t.topic_id for t in topics]),
    )


def save_topics_json(topics: PaperTopics, output_path: str):
    """Save extracted topics to a JSON file."""
    data = {
        "paper_summary": topics.paper_summary,
        "topics": [
            {
                "topic_id": t.topic_id,
                "title": t.title,
                "core_idea": t.core_idea,
                "why_it_matters": t.why_it_matters,
                "controversy_level": t.controversy_level,
                "source_section": t.source_section,
                "difficulty": t.difficulty,
            }
            for t in topics.topics
        ],
        "recommended_order": topics.recommended_order,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📝 Topics saved to: {output_path}")


def load_topics_json(input_path: str) -> PaperTopics:
    """Load topics from a JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    topics = [
        Topic(
            topic_id=t["topic_id"],
            title=t["title"],
            core_idea=t["core_idea"],
            why_it_matters=t["why_it_matters"],
            controversy_level=t["controversy_level"],
            source_section=t["source_section"],
            difficulty=t["difficulty"],
        )
        for t in data["topics"]
    ]
    
    return PaperTopics(
        paper_summary=data["paper_summary"],
        topics=topics,
        recommended_order=data.get("recommended_order", [t.topic_id for t in topics]),
    )


if __name__ == "__main__":
    # Quick test
    from pdf_parser import extract_text_from_pdf
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        text = extract_text_from_pdf(pdf_path)
        topics = extract_topics(text)
        
        print(f"\n📄 Paper Summary: {topics.paper_summary}")
        print(f"\n📋 Found {len(topics.topics)} topics:")
        for t in topics.topics:
            print(f"  {t.topic_id}. {t.title} (difficulty: {t.difficulty})")
        print(f"\n📖 Recommended order: {topics.recommended_order}")
