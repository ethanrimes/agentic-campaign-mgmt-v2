# Living Knowledge Database UI

Next.js-based web interface for the Social Media Agent Framework.

## Features

- **Content Seed Tabs**: Browse news events, trends, and ungrounded ideas
- **Platform Tabs**: View Facebook and Instagram posts
- **Insights**: Access engagement analysis reports
- **Expandable Cards**: Click any item to see full details and content timeline
- **Real-time Data**: Fetches latest data from Supabase

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
```bash
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials
```

3. **Run development server:**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home dashboard
│   ├── news-events/       # News event seeds
│   ├── trends/            # Trend seeds
│   ├── ungrounded/        # Ungrounded seeds
│   ├── facebook/          # Facebook posts
│   ├── instagram/         # Instagram posts
│   └── insights/          # Insight reports
├── components/            # React components
│   ├── layout/           # Navigation, header
│   ├── seeds/            # Seed card components
│   ├── posts/            # Post card components
│   ├── insights/         # Insight card components
│   └── common/           # Shared components
├── lib/                   # Utilities
│   ├── supabase.ts       # Supabase client
│   ├── api.ts            # Data fetching functions
│   └── utils.ts          # Helper functions
└── types/                 # TypeScript types
```

## Key Components

### ExpandableCard
Generic expandable card component used throughout the app. Click to expand/collapse.

### SeedTimeline
Shows content creation timeline for a seed (tasks and posts).

### PostCard
Displays completed posts with media, metadata, and publishing status.

### InsightReportCard
Shows insight reports with tool calls and findings.

## Building for Production

```bash
npm run build
npm start
```

## Deployment

Deploy to Vercel, Netlify, or any platform supporting Next.js:

1. Connect your Git repository
2. Set environment variables in platform settings
3. Deploy!

## Technologies

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Supabase** for backend
- **Lucide React** for icons
- **date-fns** for date formatting
