# Supabase Read-Only Anonymous Access Setup

This directory contains scripts to configure your Supabase database so that the anonymous key (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) has **read-only** access to all tables.

## What This Does

The scripts will:
1. Enable Row Level Security (RLS) on all tables
2. Create policies that allow the `anon` role to only SELECT (read) data
3. Prevent INSERT, UPDATE, and DELETE operations using the anonymous key

## Files

- `setup_read_only_anon_policies.sql` - SQL script with all the configuration
- `setup_read_only_anon.py` - Python script to execute the configuration automatically

## Usage

### Option 1: Automated Setup (Recommended)

Run the Python script:

```bash
python scripts/setup_read_only_anon.py
```

The script will:
- Prompt you for your database connection string (if not in environment)
- Connect to your database
- Apply all RLS policies
- Verify the configuration

**Note:** You'll need your database connection string from:
- Supabase Dashboard → Project Settings → Database → Connection string (URI format)
- Make sure to replace `[YOUR-PASSWORD]` with your actual password

You can also set it as an environment variable:
```bash
export DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres"
```

### Option 2: Manual Setup (Supabase Dashboard)

1. Open your Supabase Dashboard
2. Go to **SQL Editor** (left sidebar)
3. Click **New query**
4. Copy the contents of `setup_read_only_anon_policies.sql`
5. Paste into the editor
6. Click **Run** (or press Cmd/Ctrl + Enter)

### Option 3: Using psql

If you have PostgreSQL client installed:

```bash
psql 'YOUR_CONNECTION_STRING' -f scripts/setup_read_only_anon_policies.sql
```

## Tables Configured

The following tables will be set to read-only for the anon role:

- `completed_posts`
- `content_creation_tasks`
- `ingested_event_sources`
- `ingested_events`
- `insight_reports`
- `media`
- `news_event_seed_sources`
- `news_event_seeds`
- `sources`
- `trend_seeds`
- `ungrounded_seeds`

## Verification

After running the script, you can verify the configuration in Supabase Dashboard:

1. Go to **Authentication** → **Policies**
2. Select each table
3. You should see a policy named `anon_read_only` that allows SELECT for the `anon` role

## Testing

To test that the configuration works:

```javascript
// This should work (reading data)
const { data, error } = await supabase
  .from('sources')
  .select('*')

// This should fail with a permission error (writing data)
const { data, error } = await supabase
  .from('sources')
  .insert({ name: 'test' })
```

## Important Notes

- **Service Role Key**: You'll need the service role key or database password to run these scripts (the anon key cannot modify its own permissions)
- **Existing Policies**: Any existing `anon_read_only` or `anon_select` policies will be replaced
- **Other Roles**: This only affects the `anon` role; authenticated users and service role are not affected

## Reverting Changes

To allow write access again for the anon role, you would need to:

1. Create additional policies for INSERT, UPDATE, DELETE
2. Or disable RLS entirely (not recommended)

Example to re-enable full access:
```sql
CREATE POLICY "anon_full_access" ON public.sources
  FOR ALL TO anon USING (true) WITH CHECK (true);
```

## Security Best Practices

- Never expose your service role key in client-side code
- Use RLS policies to control data access
- For write operations, use authenticated users with proper permissions
- Regularly audit your RLS policies
