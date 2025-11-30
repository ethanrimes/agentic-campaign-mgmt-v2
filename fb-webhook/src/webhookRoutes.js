// fb-webhook/src/webhookRoutes.js

/**
 * Webhook Routes
 *
 * Express routes for Facebook webhook verification and event handling.
 */

const express = require("express");
const { config } = require("./config");
const { handleCommentEvent } = require("./commentHandler");
const { getAllAssets } = require("./businessAssets");

const router = express.Router();

/**
 * GET /webhook - Webhook verification endpoint
 *
 * Facebook sends a GET request to verify the webhook URL.
 */
router.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  console.log("GET /webhook - Verification request:", {
    mode,
    token: token ? "***" : undefined,
    challenge: challenge ? "present" : undefined,
  });

  if (mode === "subscribe" && token === config.verifyToken) {
    console.log("Webhook verified successfully");
    res.status(200).send(challenge);
  } else {
    console.log("Verification failed - invalid token or mode");
    res.sendStatus(403);
  }
});

/**
 * POST /webhook - Webhook event handler
 *
 * Facebook sends POST requests with event data.
 */
router.post("/webhook", async (req, res) => {
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
    const pageId = entry.id;
    console.log(`\nProcessing entry for Page ID: ${pageId}`);

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
        console.log("Comment event detected");
        await handleCommentEvent(value, pageId);
      } else {
        console.log(`Skipping non-comment item: ${value.item}`);
      }
    }
  }

  console.log("=".repeat(80) + "\n");
});

/**
 * GET /health - Health check endpoint
 */
router.get("/health", (req, res) => {
  const assets = getAllAssets();
  res.json({
    status: "ok",
    service: "Facebook Webhook Server",
    timestamp: new Date().toISOString(),
    businessAssets: {
      loaded: assets.length,
      pages: assets.map((a) => ({
        id: a.id,
        name: a.name,
        facebookPageId: a.facebookPageId,
      })),
    },
  });
});

/**
 * GET /reload - Reload business assets from database
 */
router.get("/reload", async (req, res) => {
  try {
    const { reloadBusinessAssets } = require("./businessAssets");
    const assets = await reloadBusinessAssets();
    res.json({
      status: "ok",
      message: "Business assets reloaded",
      count: assets.length,
    });
  } catch (error) {
    res.status(500).json({
      status: "error",
      message: error.message,
    });
  }
});

module.exports = router;
