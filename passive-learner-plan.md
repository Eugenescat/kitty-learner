# RedNote-Style Paper Learning Tool

## Overview

**Goal**: Transform PDFs/papers into a scrollable social-media-style feed with AI agents discussing the content, so you engage with papers instead of browsing real RedNote.

**Scope**: Personal tool, single user, minimal infrastructure.

**Core Insight**: Hijack your own attention patterns—if your brain wants to scroll a feed, give it a feed that's actually useful.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         INPUT                               │
│  PDF / Paper / Document                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSOR                       │
│  1. Extract text from PDF                                   │
│  2. Split into semantic chunks (by section/paragraph)       │
│  3. Identify key concepts, claims, findings                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                       │
│  For each chunk/concept:                                    │
│    1. Select 1-3 agents to "post" about it                  │
│    2. Generate post content in agent's voice                │
│    3. Select other agents to reply                          │
│    4. Generate reply thread                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    FEED GENERATOR                           │
│  1. Assemble posts into feed order (some randomization)     │
│  2. Render to HTML with RedNote-style cards                 │
│  3. Output static HTML file                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                         OUTPUT                              │
│  Scrollable HTML feed you open in browser                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Personas

Define 5-6 distinct characters. Each has a **voice**, **focus**, and **interaction style**:

| Agent job-"nickname" | Personality | Focus | Example Post Style |
|-------|-------------|-------|-------------------|
| **AI专业本科生但是知识广博 “曲奇脆脆猪”** | Earnest, thorough | Key concepts & definitions | "Let me break down what the author means by X..." |
| **互联网产品经理 “吃西瓜的狐狸”**  | Skeptical, contrarian | Weaknesses, assumptions | "But wait, doesn't this completely ignore...?" |
| **资深开发工程师 “鸡肋哥”** | Practical, relatable | Real-world applications | "So basically this means for us in industry..." |
| **科技自媒体编辑 “小六AIGC”** | Humorous, casual | Analogies & memes | "This is literally like when you..." |
| **第五年还没毕业的博士生 “卡刃大师”** | Authoritative, connecting | Related work, big picture | "This reminds me of Smith et al.'s work on..." |
| **想进入AI行业的文科生 “海参难吃”** | Curious, naive | Basic questions | "Sorry dumb question but why does X matter?" |

### Persona Design Notes

- Each agent should have a consistent avatar and visual style
- Agents can have "catchphrases" or recurring patterns to make them memorable
- Mix of Chinese and English names to feel like real RedNote
- Consider adding 1-2 more agents based on your own learning style

---

## File Structure

```
rednote-learner/
├── main.py                 # Entry point: CLI to process a PDF
├── pdf_parser.py           # PDF → text chunks
├── agents.py               # Agent persona definitions & prompts
├── generator.py            # LLM calls to generate posts/replies
├── feed_builder.py         # Assemble posts into feed structure
├── templates/
│   └── feed.html           # Jinja2 template for output
├── output/                 # Generated HTML feeds go here
├── requirements.txt
└── .env                    # OpenAI API key
```

---

## Implementation Phases

### Phase 1: Minimal Working Version

**Goal**: PDF in → scrollable feed out. Ugly is fine, just works.

**Tasks**:
- [ ] PDF text extraction (pymupdf)
- [ ] Simple chunking (by paragraphs or fixed size)
- [ ] 2-3 agent personas hardcoded
- [ ] Generate 1 post per chunk + 1-2 replies
- [ ] Basic HTML output (cards in a column)
- [ ] CLI: `python main.py paper.pdf` → opens `output/feed.html`

**Validation**: Run on one of your papers. Do you actually scroll through it?

---

### Phase 2: Make It Feel Good

**Goal**: UI that actually competes with RedNote's dopamine.

**Tasks**:
- [ ] RedNote-style card design (images, avatars, proper typography)
- [ ] Agent avatar images (can use static illustrations)
- [ ] Add "likes" count (randomly generated, just for feel)
- [ ] Better chunking: extract sections, headings, key claims
- [ ] Randomize feed order so it feels less predictable
- [ ] Add cover images for posts (optional: generate with DALL-E, or use abstract placeholders)

---

### Phase 3: Smarter Content

**Goal**: Posts that are actually interesting, not just summaries.

**Tasks**:
- [ ] Improve prompts for each agent to be more distinctive
- [ ] Add "hot takes" and "controversial opinions" from 杠精老王
- [ ] Agent replies actually respond to each other (not generic)
- [ ] Extract figures/tables from PDF and reference them
- [ ] Add "knowledge test" posts: agents quiz you on content

---

### Phase 4: Quality of Life

**Goal**: Sustainable daily use.

**Tasks**:
- [ ] Batch processing: drop multiple PDFs, get combined feed
- [ ] History: save generated feeds, browse past papers
- [ ] Regenerate: button to get fresh takes on same paper
- [ ] Local LLM option (Ollama) for free/offline use
- [ ] Browser auto-open when feed is ready

---

### Phase 5: Addiction Features (Optional)

**Goal**: Make it as sticky as real RedNote.

**Tasks**:
- [ ] "New posts" notification when you haven't checked in a while
- [ ] Infinite scroll: load more posts as you scroll
- [ ] User can reply to agents, agents respond
- [ ] Daily digest: agents "discuss" papers you uploaded this week
- [ ] Block real RedNote until you've scrolled X paper-posts (browser extension)

---

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.11+ | Fast to prototype, good libraries |
| PDF Parsing | `pymupdf` (fitz) | Reliable, handles most PDFs |
| LLM | OpenAI API (gpt-4o-mini) | Good quality, cheap for personal use |
| Templating | Jinja2 | Simple, Python-native |
| CSS | Tailwind (CDN) | Quick styling, no build step |
| Output | Static HTML | No server needed, just open in browser |

### Alternative Options

- **LLM**: Claude API, or local Ollama (free but lower quality)
- **PDF Parsing**: `unstructured`, `marker` for complex academic papers
- **Frontend**: Could later upgrade to React/Vue if you want interactivity

---

## Key Technical Decisions

### Chunking Strategy

**Option A: Fixed size** (every ~500 tokens)
- Pros: Simple, predictable
- Cons: Might cut mid-thought, loses document structure

**Option B: By structure** (sections, paragraphs, headings)
- Pros: More coherent chunks, respects author's organization
- Cons: Needs smarter parsing, varies by document

**Recommendation**: Start with Option A, upgrade to B in Phase 3.

### LLM Call Strategy

Each post = 1 LLM call. Each reply = 1 LLM call.

For a 10-page paper:
- ~20 chunks → 20 posts → 20 calls
- ~2 replies each → 40 calls
- **Total: ~60 calls per paper**

**Cost Estimates**:
- GPT-4o-mini: ~$0.01-0.02 per paper
- GPT-4o: ~$0.10-0.20 per paper
- Local Ollama: Free

### Persona Consistency

**Problem**: LLMs drift from persona over many calls.

**Solution**: Include full persona description in system prompt for every call. Stateless but consistent.

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Still prefer real RedNote | High | Make Phase 2 a priority; dopamine is in the details |
| PDF parsing fails on complex papers | Medium | Fallback to copy-paste text input |
| Agent posts feel repetitive | Medium | Add randomness, vary post types (question, take, summary, meme) |
| Costs add up | Low | Use GPT-4o-mini, or switch to local Ollama |
| Lose interest in building it | Medium | Phase 1 must be achievable in one evening |

---

## Success Criteria

- **Phase 1 success**: You run it on a paper you've been avoiding, and you scroll through the whole feed.
- **Overall success**: You reach for this tool instead of RedNote when procrastinating, at least sometimes.

---

## Open Questions

1. Should agents post in Chinese or English? (Match the paper language? Always Chinese for RedNote feel?)
2. How long should each post be? (Short and punchy vs. detailed?)
3. Should there be a "summary" post at the end that ties everything together?
4. Do you want audio/TTS so you can listen instead of read?

---

## Notes / Ideas

<!-- Add your own notes here as you revise -->

- 
- 
- 

