# Tool Integration Tests

This directory contains comprehensive integration tests for all Langchain tools used in the social media manager system. These tests use real APIs and database connections to verify end-to-end functionality.

## Test Files

- `test_knowledge_base_tools.py` - Integration tests for knowledge base access tools (requires Supabase)
- `test_engagement_tools.py` - Integration tests for Meta engagement API tools (requires Meta API credentials)
- `test_facebook_scraper_tools.py` - Integration tests for Facebook scraping tools (requires RapidAPI)
- `test_instagram_scraper_tools.py` - Integration tests for Instagram scraping tools (requires RapidAPI)
- `test_media_generation_tools.py` - Integration tests for AI image and video generation (requires Wavespeed API)

## Running Tests

### Prerequisites

These are integration tests that require:
- Configured `.env` file with all necessary API credentials
- Active Supabase database connection
- Valid API keys for external services

### Run all integration tests:
```bash
pytest backend/tools/tests/ -v -m integration
```

### Run specific test file:
```bash
pytest backend/tools/tests/test_knowledge_base_tools.py -v
```

### Run only tests that don't require external APIs:
```bash
pytest backend/tools/tests/test_knowledge_base_tools.py -v
```

### Run tests with specific markers:
```bash
# Run only tests requiring Meta API
pytest backend/tools/tests/ -v -m requires_meta

# Run only tests requiring RapidAPI
pytest backend/tools/tests/ -v -m requires_rapidapi

# Run only tests requiring Wavespeed
pytest backend/tools/tests/ -v -m requires_wavespeed
```

### Run with coverage:
```bash
pytest backend/tools/tests/ --cov=backend.tools --cov-report=html
```

## Test Structure

Each test file follows this structure:

1. **Real API Integration**: Tests make actual API calls to external services
2. **Database Integration**: Tests create and clean up real database records
3. **Error Handling**: Tests verify graceful handling of edge cases
4. **Workflow Tests**: Tests verify complete end-to-end workflows
5. **Concurrent Execution**: Tests verify tools work correctly with async/concurrent operations

## Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.integration` - All tests are integration tests
- `@pytest.mark.requires_meta` - Tests requiring Meta API credentials
- `@pytest.mark.requires_rapidapi` - Tests requiring RapidAPI credentials
- `@pytest.mark.requires_wavespeed` - Tests requiring Wavespeed API credentials

Tests are automatically skipped if required credentials are not configured.

## What These Tests Validate

1. **Real API Calls**: Tools successfully interact with external APIs
2. **Database Operations**: Tools correctly read/write to Supabase
3. **Error Handling**: Tools handle API errors and edge cases gracefully
4. **Data Formatting**: Tools return properly formatted, usable results
5. **Async Operations**: Tools work correctly with async/await patterns
6. **Concurrent Execution**: Multiple tools can run concurrently without issues

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `db_client` - Supabase database client
- `test_news_seed` - Creates and cleans up test news event seeds
- `test_trend_seed` - Creates and cleans up test trend seeds
- `test_ungrounded_seed` - Creates and cleans up test ungrounded seeds
- `test_insight_report` - Creates and cleans up test insight reports
- `cleanup_generated_media` - Cleans up media generated during tests
- `test_page_id` - Facebook Page ID for testing
- `test_instagram_id` - Instagram Business Account ID for testing

## Important Notes

### API Costs
- **Media generation tests** will incur real API costs when run
- **Scraper tests** may count against RapidAPI quotas
- Consider running expensive tests selectively

### Test Data
- Tests create real database records (cleaned up automatically)
- Tests use actual API endpoints and may retrieve real data
- Test data is marked with "Integration Test" prefixes for identification

### Rate Limiting
- Some APIs have rate limits
- Running all tests in parallel may hit rate limits
- Consider using `pytest-xdist` with limited workers if needed

### Environment Variables Required

For full test coverage, configure these in your `.env`:

```bash
# Supabase (required for knowledge base tests)
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key

# Meta API (required for engagement tests)
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
app_users_instagram_account_id=your_ig_id

# RapidAPI (required for scraper tests)
RAPIDAPI_KEY=your_key

# Wavespeed (required for media generation tests)
WAVESPEED_API_KEY=your_key
```

## Adding New Tests

When adding new tools:

1. Create integration tests that use real APIs
2. Add appropriate pytest markers for dependencies
3. Create fixtures for test data setup/cleanup
4. Test at minimum:
   - Success case with real API calls
   - Error handling with graceful degradation
   - Edge cases (empty results, invalid inputs)
   - Sync method raises NotImplementedError
5. Use `cleanup_generated_media` fixture for tests that create persistent data
6. Document any API costs in test docstrings

## Dependencies

Tests require:
- `pytest`
- `pytest-asyncio` (for async test support)
- `pytest-cov` (optional, for coverage reports)
- All backend dependencies (supabase, API clients, etc.)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov
```

## Continuous Integration

For CI/CD pipelines:
- Skip tests requiring paid APIs by default
- Use environment variable gates for optional test suites
- Run knowledge base tests (free) on every commit
- Run full integration suite on release branches only
