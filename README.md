# Social Media Agent Framework

An autonomous, multi-agent system for managing social media content on Facebook and Instagram. The framework discovers content opportunities, plans weekly strategies, generates posts with AI media, verifies content safety, and publishes automatically.

> **Research Project**: This framework is developed as part of a thesis exploring autonomous AI agents for social media management. See [Research Contributions](#research-contributions) below.

## Key Features

- **Multi-agent architecture**: Specialized agents for news discovery, trend analysis, content planning, creation, verification, and publishing
- **AI-powered media generation**: Automatic image and video creation via Wavespeed AI
- **Content verification**: Safety checks using Gemini 2.5 Flash before publishing
- **Engagement management**: Automated comment monitoring and response generation
- **Multi-tenancy**: Manage multiple social media accounts from one deployment
- **Configurable guardrails**: Min/max constraints for posts, seeds, and media budgets

## Architecture Overview

```
Content Seeds (News, Trends, Ideas)
            ↓
    Insights Agent (analyzes what works)
            ↓
    Planner Agent (creates weekly plan)
            ↓
    Content Creation Agent (generates posts + media)
            ↓
    Verifier Agent (safety checks)
            ↓
    Publishers (Facebook + Instagram)
            ↓
    Comment Responder (engagement)
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Supabase account
- API keys: OpenAI, Perplexity, Gemini, Wavespeed, RapidAPI, Meta

### Installation

```bash
# Clone and setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
python scripts/run_migrations.py
```

### Running

```bash
# Start automated scheduler (runs all pipelines)
python -m backend.scheduler

# Or run individual commands
python -m backend.cli.main --help
```

### Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Documentation

- **[SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)** - Detailed system documentation including:
  - **Research contributions and novel techniques**
  - Complete agent descriptions and responsibilities
  - Content pipeline flow and data model
  - Database schema reference
  - External service integrations
  - Scheduling configuration
  - CLI command reference

## Research Contributions

This framework presents several novel contributions to autonomous AI agents:

| Contribution | Description |
|-------------|-------------|
| **End-to-End Autonomous Pipeline** | Fully autonomous content lifecycle from discovery to publication |
| **Living Knowledge Database** | Heterogeneous content seeds (news, trends, creative) unified for planning |
| **LLM Semantic Deduplication** | Using LLMs to deduplicate news events through reasoning |
| **Guardrail-Constrained Planning** | Hybrid LLM + validator with automatic retry for constraint satisfaction |
| **Unified Cross-Platform Format** | Atomic operations for multi-platform posting |
| **Verification Groups** | Primary/secondary inheritance for efficient content verification |
| **Multimodal Safety Verification** | Pre-publication checklist verification using Gemini |
| **Insights-Driven Adaptation** | Feedback loop where engagement metrics inform strategy |
| **Tool-Augmented Discovery** | Autonomous trend research using tool-equipped LLMs |
| **Multi-Tenant Architecture** | SaaS-ready design with data isolation |
| **Declarative Media Specs** | Separation of media planning (LLM) from execution (services) |

For detailed descriptions of each contribution, see [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md#research-contributions).

## Project Structure

```
├── backend/
│   ├── agents/          # AI agents (insights, planner, content, verifier, etc.)
│   ├── cli/             # Command-line interface
│   ├── config/          # Settings and guardrails
│   ├── database/        # Supabase repositories and migrations
│   ├── models/          # Pydantic schemas
│   ├── services/        # External APIs (Meta, Wavespeed, RapidAPI)
│   └── scheduler.py     # Automated job scheduler
├── frontend/            # Next.js dashboard
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## CLI Examples

```bash
# Ingest news events
python -m backend.cli.main news-events ingest-perplexity --business-asset-id <id>

# Discover trends
python -m backend.cli.main trends discover --business-asset-id <id>

# Run full planning pipeline
python -m backend.cli.main planner run --business-asset-id <id>

# Create content for pending tasks
python -m backend.cli.main content create-all --business-asset-id <id>

# Verify and publish
python -m backend.cli.main verifier verify-all --business-asset-id <id>
python -m backend.cli.main publish all --business-asset-id <id>
```

## Configuration

Key settings in `.env`:

```env
# Guardrails
MIN_POSTS_PER_WEEK=3
MAX_POSTS_PER_WEEK=15
MAX_IMAGES_PER_WEEK=20
MAX_VIDEOS_PER_WEEK=5

# Model
DEFAULT_MODEL_NAME=gpt-4o-mini

# Multi-tenancy
BUSINESS_ASSETS=asset1,asset2
```

## Tech Stack

- **Backend**: Python, LangChain, Pydantic
- **Database**: Supabase (PostgreSQL)
- **AI Models**: OpenAI/Anthropic (reasoning), Gemini (verification), Wavespeed (media)
- **APIs**: Meta Graph API, Perplexity, RapidAPI
- **Frontend**: Next.js, TailwindCSS
- **Scheduler**: APScheduler

## License

MIT License
