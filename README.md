# Social Media Agent Framework

An agentic framework for managing social media (Facebook + Instagram) designed to maximize user engagement through AI-powered content generation, planning, and publishing.

## 🎯 Overview

This framework uses multiple specialized AI agents to:
1. **Discover** relevant content seeds from news, social media trends, and creative ideas
2. **Analyze** what content resonates with your audience
3. **Plan** weekly content strategies within defined guardrails
4. **Create** engaging posts with AI-generated images and videos
5. **Publish** content automatically to Facebook and Instagram

## ⚡ Quick Start

**NEW TO THIS PROJECT?** Follow these guides in order:

1. 📋 **[QUICKSTART_CHECKLIST.md](docs/QUICKSTART_CHECKLIST.md)** - Complete setup checklist
2. 🗄️ **[DATABASE_SETUP_GUIDE.md](docs/DATABASE_SETUP_GUIDE.md)** - Step-by-step database configuration
3. 🧪 **[REMAINING_IMPLEMENTATION.md](docs/REMAINING_IMPLEMENTATION.md)** - Testing and validation guide
4. 📊 **[IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md)** - Current status and architecture

**Estimated time to get operational**: 3-4 hours

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE INGESTION                       │
├──────────────────┬──────────────────┬──────────────────────┤
│  News Events     │  Trend Discovery │  Ungrounded Ideas    │
│  • Perplexity    │  • IG/FB Scraper│  • Creative Agent    │
│  • Deep Research │  • Trend Analysis│                      │
│  • Deduplication │                  │                      │
└──────────────────┴──────────────────┴──────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              LIVING KNOWLEDGE DATABASE (Supabase)            │
│  • News Event Seeds  • Trend Seeds  • Ungrounded Seeds      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      INSIGHTS AGENT                          │
│  Analyzes engagement metrics to learn what works            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      PLANNER AGENT                           │
│  Creates weekly content plan with guardrails                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 CONTENT CREATION AGENT                       │
│  Generates posts with AI images/videos (Wavespeed)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────────────────────────────┐
│  FB Publisher    │         IG Publisher                      │
│  • Feed Posts    │  • Image Posts    • Reels                │
│  • Videos        │  • Carousels      • Stories              │
└──────────────────┴──────────────────────────────────────────┘
```

### Agent Descriptions

#### 1. News Event Seed Agents
- **Perplexity Sonar**: Quickly finds recent news events with structured output
- **Deep Research (o4-mini)**: Performs in-depth research on topics
- **Research Parser**: Converts deep research reports to standardized format
- **Deduplicator**: Consolidates duplicate events into canonical seeds

#### 2. Trend Seed Agent
- Uses RapidAPI to scrape Facebook/Instagram
- Identifies trending hashtags, viral posts, and popular content
- Synthesizes findings into trend seeds for content creation

#### 3. Ungrounded Seed Agent
- Generates creative content ideas not tied to news or trends
- Ensures content diversity and originality
- Examples provided in prompt for inspiration

#### 4. Insights Agent
- Fetches engagement metrics (likes, comments, shares, reach)
- Analyzes which content types perform best
- Produces timestamped reports used by planner

#### 5. Planner Agent
- Reviews available content seeds and insights
- Creates weekly content plan
- Validates against guardrails (min/max posts, images, videos)
- Retries if plan violates constraints

#### 6. Content Creation Agent
- Reads content creation tasks from database
- Generates images/videos using Wavespeed AI
- Uploads media to Supabase storage
- Creates completed post objects ready for publishing

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Supabase account
- API keys for:
  - OpenAI (or Gemini/Anthropic)
  - Perplexity AI
  - Wavespeed AI
  - RapidAPI (for social media scraping)
  - Meta/Facebook (Page Access Token, Instagram User Access Token)

### Installation

1. **Clone the repository**
```bash
cd agentic-campaign-mgmt-v2
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Set up database**
```bash
# Run migrations
python scripts/run_migrations.py

# (Optional) Seed test data
python scripts/seed_test_data.py
```

5. **Initialize Supabase storage bucket**
```bash
python scripts/setup_database.py
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all configuration options. Key settings:

```env
# Target Audience (North Star)
TARGET_AUDIENCE="College students at the University of Pennsylvania interested in campus news, events, and local culture"

# Content Guardrails
MIN_POSTS_PER_WEEK=3
MAX_POSTS_PER_WEEK=15
MIN_CONTENT_SEEDS_PER_WEEK=2
MAX_CONTENT_SEEDS_PER_WEEK=8
MIN_VIDEOS_PER_WEEK=0
MAX_VIDEOS_PER_WEEK=5
MIN_IMAGES_PER_WEEK=1
MAX_IMAGES_PER_WEEK=20

# Model Provider
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4o-mini
```

### Guardrails

Guardrails ensure sustainable content production:
- **Min/Max Posts**: Prevents overposting or underposting
- **Min/Max Seeds**: Ensures content diversity
- **Media Budgets**: Controls AI generation costs

Modify in `.env` or `backend/config/guardrails_config.py`

## 📝 CLI Commands

### News Event Ingestion

```bash
# Ingest events via Perplexity Sonar
python -m backend.cli.main news-events ingest-perplexity --topic "Philadelphia news"

# Ingest via ChatGPT Deep Research
python -m backend.cli.main news-events ingest-deep-research --query "Recent SEPTA updates"

# Run deduplication
python -m backend.cli.main news-events deduplicate --business-asset-id penndailybuzz
```

### Trend Discovery

```bash
# Discover trends
python -m backend.cli.main trends discover --business-asset-id penndailybuzz
```

### Ungrounded Seed Generation

```bash
# Generate creative content ideas
python -m backend.cli.main ungrounded generate --count 1 --business-asset-id penndailybuzz
```

### Insights Analysis

```bash
# Run insights agent
python -m backend.cli.main insights analyze --days 14 --business-asset-id penndailybuzz
```

### Content Planning

```bash
# Run planner agent (with retries)
python -m backend.cli.main planner run --max-retries 3 --business-asset-id penndailybuzz
```

### Content Creation

```bash
# Create content for all pending tasks
python -m backend.cli.main content create-all --business-asset-id penndailybuzz

# Create content for specific task
python -m backend.cli.main content create --task-id abc-123-def --business-asset-id penndailybuzz
```

### Publishing

```bash
# Publish pending Facebook posts
python -m backend.cli.main publish facebook --business-asset-id penndailybuzz

# Publish pending Instagram posts
python -m backend.cli.main publish instagram

# Publish all
python -m backend.cli.main publish all --business-asset-id penndailybuzz
```

### Comment Responding

1. **`comments check-instagram`**
   ```bash
   python -m backend.cli.main comments check-instagram --max-media 20
   ```
   Manually trigger Instagram comment check

2. **`comments respond`**
   ```bash
   python -m backend.cli.main comments respond --platform all --limit 10
   ```
   Process pending comments and post responses

3. **`comments test-responder`**
   ```bash
   python -m backend.cli.main comments test-responder --platform instagram COMMENT_ID
   ```
   Test response generation without posting (for debugging)



## 🤖 Scheduling with Cron

For automated operation, schedule agents with cron:

```cron
# News ingestion (daily at 6 AM)
0 6 * * * cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main news-events ingest-perplexity --topic "Philadelphia news"

# Trend discovery (daily at 8 AM)
0 8 * * * cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main trends discover --keyword "UPenn"

# Insights analysis (weekly on Monday at 9 AM)
0 9 * * 1 cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main insights analyze --days 7

# Content planning (weekly on Monday at 10 AM)
0 10 * * 1 cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main planner run --max-retries 3

# Content creation (daily at 11 AM)
0 11 * * * cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main content create-all

# Publishing (every 6 hours)
0 */6 * * * cd /path/to/project && /path/to/venv/bin/python -m backend.cli.main publish all
```

## 🖥️ Living Knowledge Database UI

### Setup

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
# Open http://localhost:3000
```

### Features

The UI provides visibility into the entire system:

**Content Seed Tabs:**
- **News Events**: View all news event seeds with sources and timeline
- **Trends**: Browse discovered trends with hashtags and referenced posts
- **Ungrounded**: See creative content ideas

**Platform Tabs:**
- **Facebook**: All Facebook posts (sorted by recency)
- **Instagram**: All Instagram posts (sorted by recency)
- Each post is expandable to show full context (task, seed, media)

**Insights Tab:**
- View insight reports with tool calls and findings
- Understand what content works with your audience

## 📊 Database Schema

### Content Seeds

**news_event_seeds**
- Canonical news events (deduplicated)
- Fields: name, description, location, start_time, end_time, sources[]

**trend_seeds**
- Social media trends
- Fields: name, description, hashtags[], posts[], users[]

**ungrounded_seeds**
- Creative content ideas
- Fields: idea, format, details

### Tasks & Posts

**content_creation_tasks**
- Tasks from planner agent
- Fields: content_seed_id, platform allocations, media budgets, status

**completed_posts**
- Finished posts ready for publishing
- Fields: task_id, platform, post_type, text, media_urls[], status

### Analytics

**insight_reports**
- Insight agent findings
- Fields: summary, findings, tool_calls[]

**planner_outputs**
- Historical plans (valid and invalid)
- Fields: allocations[], reasoning, is_valid

## 🔌 API Integrations

### Meta Graph API
- **Facebook**: Page posts (images, carousels, videos, text)
- **Instagram**: Image posts, carousels, reels, stories
- **Engagement**: Fetch likes, comments, shares, reach

### Wavespeed AI
- **Image Generation**: SDXL-LoRA (1024x1024)
- **Video Generation**: WAN-2.2 I2V (720p)

### OpenAI (Deep Research)
- Uses Responses API for o4-mini deep research
- Requires special handling (not compatible with Langchain)

### Perplexity Sonar
- Structured output for news events
- Fast, citation-rich responses

### RapidAPI
- Instagram scraping (posts, users, locations, hashtags)
- Facebook scraping (posts, pages, groups)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/unit/agents/test_planner_agent.py
```

## 🚢 Deployment

### Render Deployment

1. **Create Render Blueprint** (`render.yaml` provided)

2. **Set Environment Variables** in Render dashboard

3. **Deploy**:
```bash
# Push to GitHub
git push origin main

# Render auto-deploys on push
```

### Database Migrations

Migrations run automatically on deployment. To run manually:

```bash
python scripts/run_migrations.py
```

## 🛠️ Development

### Adding a New Agent

1. Create agent file in `backend/agents/`
2. Create system prompt in `prompts/` subdirectory
3. Register prompt in `backend/config/prompts.py`
4. Create CLI command in `backend/cli/`
5. Document in README

### Adding a New Content Seed Type

1. Define model in `backend/models/seeds.py`
2. Create migration in `backend/database/migrations/`
3. Create repository in `backend/database/repositories/`
4. Update `content_creation_tasks` enum in migration
5. Update planner agent logic

### Extending the Frontend

Frontend is Next.js with:
- **App Router** (app/ directory)
- **Supabase client** for data fetching
- **TailwindCSS** for styling

Add new tabs by creating pages in `frontend/app/`

## 📚 Project Structure

```
agentic-campaign-mgmt-v2/
├── backend/               # Python backend
│   ├── agents/           # All AI agents
│   ├── config/           # Configuration & prompts
│   ├── database/         # Supabase client & repositories
│   ├── models/           # Pydantic schemas
│   ├── services/         # External API integrations
│   ├── tools/            # Langchain tool wrappers
│   ├── cli/              # CLI commands
│   └── utils/            # Utilities
├── frontend/             # Next.js UI
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── types/            # TypeScript types
├── scripts/              # Deployment & utility scripts
├── tests/                # Test suite
└── docs/                 # Additional documentation
```

## 🤝 Contributing

This is a research project exploring autonomous AI agents. Contributions welcome!

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Langchain for agent orchestration
- Supabase for backend infrastructure
- Meta for Graph API
- Wavespeed AI for media generation
- OpenAI, Perplexity, and Anthropic for LLMs

---

**Note**: This framework is designed for research purposes to study AI agent capabilities in autonomous content management. For production use, implement proper content moderation, human-in-the-loop approval, and rate limiting.



# Lines of Code

```
(venv) ethan@ist-12739 social-media-manager-v2 % cloc . \
--not-match-d='(^|/)(__pycache__|\.next|\.pytest_cache|node_modules|venv)($|/)' \
--exclude-list-file=<(printf "migrations.md\nSCHEDULER_README.md\ntools/tests/README.md\nfrontend/package-lock.json\nfb-webhook/package-lock.json")
     194 text files.
     189 unique files.                                          
    4115 files ignored.

cloc . --not-match-d='(^|/)(__pycache__|\.next|\.pytest_cache|node_modules|venv)($|/)' --exclude-list-file=<(printf "migrations.md\nSCHEDULER_README.md\ntools/tests/README.md\nfrontend/package-lock.json\nfb-webhook/package-lock.json")

github.com/AlDanial/cloc v 2.06  T=0.35 s (531.2 files/s, 82908.9 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                         107           3548           3908          10959
TypeScript                      32            393             99           4322
Markdown                        12            950              0           2852
SQL                             18            138            178            456
Text                             8            151              0            445
JavaScript                       4             52             42            297
CSS                              1             32             12            159
JSON                             4              0              0            121
TOML                             1              7              0             66
-------------------------------------------------------------------------------
SUM:                           187           5271           4239          19677
-------------------------------------------------------------------------------
```