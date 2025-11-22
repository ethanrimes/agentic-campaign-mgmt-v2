// fb-webhook/index.js

const express = require("express");
const bodyParser = require("body-parser");
const { createClient } = require("@supabase/supabase-js");
require("dotenv").config({ path: "../.env" });  // Load from root .env file

const app = express();

// Environment variables
const VERIFY_TOKEN = process.env.FACEBOOK_WEBHOOK_VERIFY_TOKEN;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const PORT = process.env.WEBHOOK_PORT || 3000;

// Validate required environment variables
if (!VERIFY_TOKEN) {
  console.error("ERROR: FACEBOOK_WEBHOOK_VERIFY_TOKEN not set in .env file");
  process.exit(1);
}
if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file");
  process.exit(1);
}

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

app.use(bodyParser.json());

// ============================================================================
// WEBHOOK VERIFICATION ENDPOINT
// ============================================================================

app.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  console.log("GET /webhook - Verification request:", {
    mode,
    token: token ? "***" : undefined,
    challenge: challenge ? "present" : undefined
  });

  if (mode === "subscribe" && token === VERIFY_TOKEN) {
    console.log("✓ Webhook verified successfully");
    res.status(200).send(challenge);
  } else {
    console.log("✗ Verification failed - invalid token or mode");
    res.sendStatus(403);
  }
});

// ============================================================================
// WEBHOOK EVENT HANDLER
// ============================================================================

app.post("/webhook", async (req, res) => {
  console.log("\n" + "=".repeat(80));
  console.log("POST /webhook - Received event");
  console.log("=".repeat(80));

  // Always respond quickly with 200 to acknowledge receipt
  res.sendStatus(200);

  const body = req.body;

  // Validate webhook payload
  if (body.object !== "page") {
    console.log("Not a page event, ignoring");
    return;
  }

  // Process each entry
  for (const entry of body.entry || []) {
    console.log(`\nProcessing entry ID: ${entry.id}`);

    // Process each change in the entry
    for (const change of entry.changes || []) {
      console.log(`Field: ${change.field}`);

      // We only care about feed changes (comments, posts, etc.)
      if (change.field !== "feed") {
        console.log(`Skipping non-feed field: ${change.field}`);
        continue;
      }

      const value = change.value;

      // Check if this is a comment event (not a post)
      if (value.item === "comment") {
        console.log("✓ Comment event detected");
        await handleCommentEvent(value);
      } else {
        console.log(`Skipping non-comment item: ${value.item}`);
      }
    }
  }

  console.log("=".repeat(80) + "\n");
});

// ============================================================================
// COMMENT EVENT HANDLER
// ============================================================================

async function handleCommentEvent(value) {
  try {
    console.log("\nHandling comment event:");
    console.log(JSON.stringify(value, null, 2));

    const commentId = value.comment_id;
    const postId = value.post_id;
    const commentText = value.message || "";
    const verb = value.verb;  // "add", "edit", or "remove"

    // Only process new comments (verb = "add")
    if (verb !== "add") {
      console.log(`Skipping comment with verb: ${verb}`);
      return;
    }

    // Extract commenter info
    const from = value.from || {};
    const commenterName = from.name || "Unknown";
    const commenterId = from.id || "unknown";

    // Extract parent_id if this is a reply
    const parentId = value.parent_id;

    // Extract timestamp
    const createdTime = value.created_time
      ? new Date(value.created_time * 1000).toISOString()
      : new Date().toISOString();

    // Prepare comment data for database
    const commentData = {
      platform: "facebook",
      comment_id: commentId,
      post_id: postId,
      comment_text: commentText,
      commenter_username: commenterName,
      commenter_id: commenterId,
      parent_comment_id: parentId || null,
      created_time: createdTime,
      like_count: 0,  // Not available in webhook payload
      permalink_url: value.permalink_url || null,
      status: "pending"
    };

    console.log("\nInserting comment to database:");
    console.log(JSON.stringify(commentData, null, 2));

    // Insert into Supabase
    const { data, error } = await supabase
      .from("platform_comments")
      .insert(commentData)
      .select();

    if (error) {
      // Check if it's a duplicate (comment_id already exists)
      if (error.code === "23505") {  // Unique violation
        console.log(`Comment ${commentId} already exists in database, skipping`);
        return;
      }

      throw error;
    }

    console.log(`✓ Successfully saved comment to database`);
    console.log(`  Database ID: ${data[0]?.id}`);
    console.log(`  Comment ID: ${commentId}`);
    console.log(`  Post ID: ${postId}`);
    console.log(`  Commenter: ${commenterName}`);
    console.log(`  Text: "${commentText.substring(0, 50)}${commentText.length > 50 ? "..." : ""}"`);

  } catch (error) {
    console.error("\n✗ Error handling comment event:");
    console.error(error);
  }
}

// ============================================================================
// HEALTH CHECK ENDPOINT
// ============================================================================

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "Facebook Webhook Server",
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log("\n" + "=".repeat(80));
  console.log("Facebook Webhook Server Started");
  console.log("=".repeat(80));
  console.log(`Port: ${PORT}`);
  console.log(`Webhook URL: http://localhost:${PORT}/webhook`);
  console.log(`Health Check: http://localhost:${PORT}/health`);
  console.log(`Verify Token: ${VERIFY_TOKEN ? "✓ Set" : "✗ Not Set"}`);
  console.log(`Supabase: ${SUPABASE_URL ? "✓ Connected" : "✗ Not Connected"}`);
  console.log("=".repeat(80) + "\n");
  console.log("Listening for Facebook webhook events...\n");
});

// ============================================================================
// ERROR HANDLING
// ============================================================================

process.on("uncaughtException", (error) => {
  console.error("Uncaught Exception:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});
