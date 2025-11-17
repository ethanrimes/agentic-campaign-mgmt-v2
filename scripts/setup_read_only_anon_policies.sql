-- Script to set up read-only permissions for the anonymous (anon) role
-- This ensures that the NEXT_PUBLIC_SUPABASE_ANON_KEY can only read data, not write

-- List of all tables to configure
DO $$
DECLARE
    table_name text;
    tables text[] := ARRAY[
        'completed_posts',
        'content_creation_tasks',
        'ingested_event_sources',
        'ingested_events',
        'insight_reports',
        'media',
        'news_event_seed_sources',
        'news_event_seeds',
        'sources',
        'trend_seeds',
        'ungrounded_seeds'
    ];
BEGIN
    FOREACH table_name IN ARRAY tables
    LOOP
        -- Enable Row Level Security on the table
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', table_name);

        -- Drop existing policies for anon role (if any)
        EXECUTE format('DROP POLICY IF EXISTS "anon_read_only" ON public.%I;', table_name);
        EXECUTE format('DROP POLICY IF EXISTS "anon_select" ON public.%I;', table_name);

        -- Create a read-only policy for the anon role
        EXECUTE format('
            CREATE POLICY "anon_read_only"
            ON public.%I
            FOR SELECT
            TO anon
            USING (true);
        ', table_name);

        RAISE NOTICE 'Configured read-only access for table: %', table_name;
    END LOOP;
END $$;

-- Verify the configuration
SELECT
    schemaname,
    tablename,
    rowsecurity as "RLS Enabled"
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'completed_posts',
    'content_creation_tasks',
    'ingested_event_sources',
    'ingested_events',
    'insight_reports',
    'media',
    'news_event_seed_sources',
    'news_event_seeds',
    'sources',
    'trend_seeds',
    'ungrounded_seeds'
)
ORDER BY tablename;

-- Show all policies for verification
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
