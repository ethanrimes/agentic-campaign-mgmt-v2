// frontend/types/index.ts

export interface NewsEventSeed {
  id: string
  name: string
  start_time: string | null
  end_time: string | null
  location: string
  description: string
  sources: Source[]
  created_at: string
}

export interface Source {
  id: string
  url: string
  key_findings: string
  found_by: string
  created_at: string
}

export interface TrendSeed {
  id: string
  name: string
  description: string
  hashtags: string[]
  posts: any[]
  users: any[]
  created_at: string
  created_by: string
}

export interface UngroundedSeed {
  id: string
  idea: string
  format: string
  details: string
  created_at: string
  created_by: string
}

export interface CompletedPost {
  id: string
  task_id: string
  // Content seed references (exactly one will be set)
  news_event_seed_id: string | null
  trend_seed_id: string | null
  ungrounded_seed_id: string | null
  platform: 'facebook' | 'instagram'
  post_type: string
  text: string
  media_urls: string[] | null
  location: string | null
  music: string | null
  hashtags: string[] | null
  status: 'pending' | 'published' | 'failed'
  scheduled_posting_time: string | null
  published_at: string | null
  platform_post_id: string | null
  platform_post_url: string | null
  error_message: string | null
  created_at: string
}

// Helper types for posts with seed data
export interface CompletedPostWithSeed extends CompletedPost {
  content_seed_id: string
  content_seed_type: 'news_event' | 'trend' | 'ungrounded'
  seed_name: string
}

export interface ContentCreationTask {
  id: string
  content_seed_id: string
  content_seed_type: 'news_event' | 'trend' | 'ungrounded'
  instagram_image_posts: number
  instagram_reel_posts: number
  facebook_feed_posts: number
  facebook_video_posts: number
  image_budget: number
  video_budget: number
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  error_message: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface InsightReport {
  id: string
  summary: string
  findings: string
  tool_calls: ToolCall[]
  created_at: string
  created_by: string
}

export interface ToolCall {
  tool_name: string
  arguments: Record<string, any>
  result: any
  timestamp: string
}
