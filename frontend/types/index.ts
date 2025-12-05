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
  tool_calls: ToolCall[]
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
  verification_status: 'unverified' | 'verified' | 'rejected' | 'manually_overridden'
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
  recommendations: string[]
  reviewed_post_ids: string[]
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

export interface VerifierResponse {
  id: string
  business_asset_id: string
  completed_post_id: string
  is_approved: boolean
  has_no_offensive_content: boolean
  has_no_misinformation: boolean | null
  reasoning: string
  issues_found: string[]
  model: string
  created_at: string
  verification_group_id?: string | null
  is_manually_overridden: boolean
  override_reason?: string | null
  overridden_at?: string | null
}

// Insights Types

export interface FacebookPageInsights {
  id: string
  business_asset_id: string
  page_id: string
  page_name: string | null
  page_picture_url: string | null
  // Page views
  page_views_total_day: number | null
  page_views_total_week: number | null
  page_views_total_days_28: number | null
  // Engagements
  page_post_engagements_day: number | null
  page_post_engagements_week: number | null
  page_post_engagements_days_28: number | null
  // Followers
  page_follows: number | null
  // Media views
  page_media_view: number | null
  page_media_view_week: number | null
  page_media_view_days_28: number | null
  // Video views
  page_video_views: number | null
  page_video_views_week: number | null
  page_video_views_days_28: number | null
  // Total reactions
  reactions_total: number | null
  metrics_fetched_at: string | null
  created_at: string
}

export interface FacebookPostInsights {
  id: string
  business_asset_id: string
  platform_post_id: string
  completed_post_id: string | null
  // Media views
  post_media_view: number | null
  // Impressions & Reach
  post_impressions: number | null
  post_impressions_unique: number | null
  post_impressions_organic: number | null
  post_impressions_organic_unique: number | null
  post_impressions_paid: number | null
  post_impressions_paid_unique: number | null
  // Reactions
  reactions_total: number | null
  reactions_like: number | null
  reactions_love: number | null
  reactions_wow: number | null
  reactions_haha: number | null
  reactions_sorry: number | null
  reactions_anger: number | null
  // Engagement
  comments: number | null
  shares: number | null
  // Clicks
  post_clicks: number | null
  post_clicks_unique: number | null
  metrics_fetched_at: string | null
  created_at: string
}

export interface FacebookVideoInsights {
  id: string
  business_asset_id: string
  video_id: string
  completed_post_id: string | null
  // View counts
  post_video_views: number | null
  post_video_views_unique: number | null
  post_video_views_organic: number | null
  post_video_views_organic_unique: number | null
  // Watch time
  post_video_view_time_ms: number | null
  post_video_avg_time_watched_ms: number | null
  video_length_ms: number | null
  // Completion rates
  post_video_complete_views_organic: number | null
  post_video_complete_views_paid: number | null
  metrics_fetched_at: string | null
  created_at: string
}

export interface InstagramAccountInsights {
  id: string
  business_asset_id: string
  instagram_account_id: string
  username: string | null
  profile_picture_url: string | null
  followers_count: number | null
  follows_count: number | null
  media_count: number | null
  // Reach metrics
  reach_day: number | null
  reach_week: number | null
  reach_days_28: number | null
  // Profile metrics
  profile_views_day: number | null
  accounts_engaged_day: number | null
  metrics_fetched_at: string | null
  created_at: string
}

export interface InstagramMediaInsights {
  id: string
  business_asset_id: string
  platform_media_id: string
  completed_post_id: string | null
  media_type: string | null
  permalink: string | null
  // Engagement metrics
  likes: number | null
  comments: number | null
  shares: number | null
  saved: number | null
  views: number | null
  // Reach & Impressions
  reach: number | null
  impressions: number | null
  // Reels specific
  ig_reels_avg_watch_time_ms: number | null
  ig_reels_video_view_total_time_ms: number | null
  metrics_fetched_at: string | null
  created_at: string
}

// Combined insights response types
export interface CachedInsights {
  facebook_page?: FacebookPageInsights | null
  facebook_posts?: FacebookPostInsights[]
  facebook_videos?: FacebookVideoInsights[]
  instagram_account?: InstagramAccountInsights | null
  instagram_media?: InstagramMediaInsights[]
}

export interface InsightsRefreshResponse {
  status: 'ok' | 'error'
  message: string
  business_asset_id?: string
  output?: string
  error?: string
  seconds_until_allowed?: number
}
