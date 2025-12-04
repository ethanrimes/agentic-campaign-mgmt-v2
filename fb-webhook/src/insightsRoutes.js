// fb-webhook/src/insightsRoutes.js

/**
 * Insights Refresh Routes
 *
 * Express routes for triggering insights refresh via the Python CLI.
 * Includes rate limiting to prevent excessive API calls.
 */

const express = require("express");
const { exec } = require("child_process");
const path = require("path");

const router = express.Router();

// Rate limiting configuration (in-memory for simplicity)
const COOLDOWN_MINUTES = parseInt(
  process.env.INSIGHTS_REFRESH_COOLDOWN_MINUTES || "5",
  10
);
const INSIGHTS_ENABLED =
  process.env.INSIGHTS_ENABLE_WEBHOOK_REFRESH !== "false";

// Track last refresh times per business_asset_id and type
const lastRefreshTimes = new Map();

/**
 * Check if refresh is allowed based on rate limiting.
 * @param {string} businessAssetId - The business asset ID
 * @param {string} refreshType - "account" or "posts"
 * @returns {Object} { allowed: boolean, secondsUntilAllowed?: number }
 */
function checkRateLimit(businessAssetId, refreshType) {
  const key = `${businessAssetId}:${refreshType}`;
  const lastRefresh = lastRefreshTimes.get(key);

  if (!lastRefresh) {
    return { allowed: true };
  }

  const now = Date.now();
  const cooldownMs = COOLDOWN_MINUTES * 60 * 1000;
  const timeSinceLastRefresh = now - lastRefresh;

  if (timeSinceLastRefresh >= cooldownMs) {
    return { allowed: true };
  }

  const secondsUntilAllowed = Math.ceil(
    (cooldownMs - timeSinceLastRefresh) / 1000
  );
  return { allowed: false, secondsUntilAllowed };
}

/**
 * Record a refresh time for rate limiting.
 * @param {string} businessAssetId - The business asset ID
 * @param {string} refreshType - "account" or "posts"
 */
function recordRefresh(businessAssetId, refreshType) {
  const key = `${businessAssetId}:${refreshType}`;
  lastRefreshTimes.set(key, Date.now());
}

/**
 * Execute a Python CLI command.
 * @param {string} command - The CLI command to run
 * @returns {Promise<{success: boolean, output?: string, error?: string}>}
 */
function runCliCommand(command) {
  return new Promise((resolve) => {
    // Determine the project root (fb-webhook is in project root)
    const projectRoot = path.resolve(__dirname, "..", "..");

    // Build the full command with virtual environment activation
    const fullCommand = `cd "${projectRoot}" && source venv/bin/activate && python -m backend.cli.main ${command}`;

    console.log(`Executing CLI command: ${command}`);

    exec(
      fullCommand,
      { shell: "/bin/bash", timeout: 120000 },
      (error, stdout, stderr) => {
        if (error) {
          console.error(`CLI command failed: ${error.message}`);
          console.error(`stderr: ${stderr}`);
          resolve({ success: false, error: error.message, output: stderr });
        } else {
          console.log(`CLI command output: ${stdout}`);
          resolve({ success: true, output: stdout });
        }
      }
    );
  });
}

/**
 * POST /insights/refresh-account - Refresh account-level insights
 *
 * Body: { business_asset_id: string }
 */
router.post("/refresh-account", async (req, res) => {
  console.log("\n" + "=".repeat(80));
  console.log("POST /insights/refresh-account");
  console.log("=".repeat(80));

  // Check if insights refresh is enabled
  if (!INSIGHTS_ENABLED) {
    console.log("Insights webhook refresh is disabled");
    return res.status(503).json({
      status: "error",
      message: "Insights refresh is disabled",
      enabled: false,
    });
  }

  const { business_asset_id } = req.body;

  if (!business_asset_id) {
    console.log("Missing business_asset_id");
    return res.status(400).json({
      status: "error",
      message: "business_asset_id is required",
    });
  }

  // Check rate limit
  const rateLimit = checkRateLimit(business_asset_id, "account");
  if (!rateLimit.allowed) {
    console.log(
      `Rate limited: ${business_asset_id} must wait ${rateLimit.secondsUntilAllowed}s`
    );
    return res.status(429).json({
      status: "error",
      message: `Rate limited. Please wait ${rateLimit.secondsUntilAllowed} seconds before refreshing again.`,
      seconds_until_allowed: rateLimit.secondsUntilAllowed,
    });
  }

  // Record this refresh attempt
  recordRefresh(business_asset_id, "account");

  // Execute the CLI command
  const result = await runCliCommand(
    `insights fetch-account --business-asset-id ${business_asset_id}`
  );

  if (result.success) {
    console.log("Account insights refresh successful");
    return res.json({
      status: "ok",
      message: "Account insights refresh started",
      business_asset_id,
      output: result.output,
    });
  } else {
    console.error("Account insights refresh failed");
    return res.status(500).json({
      status: "error",
      message: "Failed to refresh account insights",
      error: result.error,
    });
  }
});

/**
 * POST /insights/refresh-posts - Refresh post-level insights
 *
 * Body: { business_asset_id: string, limit?: number, days_back?: number }
 */
router.post("/refresh-posts", async (req, res) => {
  console.log("\n" + "=".repeat(80));
  console.log("POST /insights/refresh-posts");
  console.log("=".repeat(80));

  // Check if insights refresh is enabled
  if (!INSIGHTS_ENABLED) {
    console.log("Insights webhook refresh is disabled");
    return res.status(503).json({
      status: "error",
      message: "Insights refresh is disabled",
      enabled: false,
    });
  }

  const { business_asset_id, limit, days_back } = req.body;

  if (!business_asset_id) {
    console.log("Missing business_asset_id");
    return res.status(400).json({
      status: "error",
      message: "business_asset_id is required",
    });
  }

  // Check rate limit
  const rateLimit = checkRateLimit(business_asset_id, "posts");
  if (!rateLimit.allowed) {
    console.log(
      `Rate limited: ${business_asset_id} must wait ${rateLimit.secondsUntilAllowed}s`
    );
    return res.status(429).json({
      status: "error",
      message: `Rate limited. Please wait ${rateLimit.secondsUntilAllowed} seconds before refreshing again.`,
      seconds_until_allowed: rateLimit.secondsUntilAllowed,
    });
  }

  // Record this refresh attempt
  recordRefresh(business_asset_id, "posts");

  // Build command with optional parameters
  let command = `insights fetch-posts --business-asset-id ${business_asset_id}`;
  if (limit) {
    command += ` --limit ${parseInt(limit, 10)}`;
  }
  if (days_back) {
    command += ` --days-back ${parseInt(days_back, 10)}`;
  }

  // Execute the CLI command
  const result = await runCliCommand(command);

  if (result.success) {
    console.log("Post insights refresh successful");
    return res.json({
      status: "ok",
      message: "Post insights refresh started",
      business_asset_id,
      output: result.output,
    });
  } else {
    console.error("Post insights refresh failed");
    return res.status(500).json({
      status: "error",
      message: "Failed to refresh post insights",
      error: result.error,
    });
  }
});

/**
 * POST /insights/refresh-all - Refresh all insights (account + posts)
 *
 * Body: { business_asset_id: string }
 */
router.post("/refresh-all", async (req, res) => {
  console.log("\n" + "=".repeat(80));
  console.log("POST /insights/refresh-all");
  console.log("=".repeat(80));

  // Check if insights refresh is enabled
  if (!INSIGHTS_ENABLED) {
    console.log("Insights webhook refresh is disabled");
    return res.status(503).json({
      status: "error",
      message: "Insights refresh is disabled",
      enabled: false,
    });
  }

  const { business_asset_id } = req.body;

  if (!business_asset_id) {
    console.log("Missing business_asset_id");
    return res.status(400).json({
      status: "error",
      message: "business_asset_id is required",
    });
  }

  // Check rate limits for both account and posts
  const accountRateLimit = checkRateLimit(business_asset_id, "account");
  const postsRateLimit = checkRateLimit(business_asset_id, "posts");

  if (!accountRateLimit.allowed || !postsRateLimit.allowed) {
    const maxWait = Math.max(
      accountRateLimit.secondsUntilAllowed || 0,
      postsRateLimit.secondsUntilAllowed || 0
    );
    console.log(`Rate limited: ${business_asset_id} must wait ${maxWait}s`);
    return res.status(429).json({
      status: "error",
      message: `Rate limited. Please wait ${maxWait} seconds before refreshing again.`,
      seconds_until_allowed: maxWait,
    });
  }

  // Record refresh for both types
  recordRefresh(business_asset_id, "account");
  recordRefresh(business_asset_id, "posts");

  // Execute the CLI command
  const result = await runCliCommand(
    `insights fetch-all --business-asset-id ${business_asset_id}`
  );

  if (result.success) {
    console.log("All insights refresh successful");
    return res.json({
      status: "ok",
      message: "All insights refresh started",
      business_asset_id,
      output: result.output,
    });
  } else {
    console.error("All insights refresh failed");
    return res.status(500).json({
      status: "error",
      message: "Failed to refresh all insights",
      error: result.error,
    });
  }
});

/**
 * GET /insights/status - Get insights refresh status and configuration
 */
router.get("/status", (req, res) => {
  res.json({
    status: "ok",
    enabled: INSIGHTS_ENABLED,
    cooldown_minutes: COOLDOWN_MINUTES,
    active_rate_limits: Object.fromEntries(lastRefreshTimes),
  });
});

module.exports = router;
