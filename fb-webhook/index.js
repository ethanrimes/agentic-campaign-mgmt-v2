// fb-webhook/index.js

/**
 * Facebook Webhook Server
 *
 * Multi-tenant webhook server for handling Facebook comment events.
 * Loads business assets from Supabase and routes events to the correct tenant.
 */

const express = require("express");
const bodyParser = require("body-parser");

const { config, validateConfig } = require("./src/config");
const { loadBusinessAssets } = require("./src/businessAssets");
const webhookRoutes = require("./src/webhookRoutes");

// Validate configuration before starting
validateConfig();

const app = express();

// Middleware
app.use(bodyParser.json());

// Routes
app.use("/", webhookRoutes);

// Error handling
process.on("uncaughtException", (error) => {
  console.error("Uncaught Exception:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});

/**
 * Start the server after loading business assets.
 */
async function startServer() {
  try {
    console.log("\n" + "=".repeat(80));
    console.log("Facebook Webhook Server Starting");
    console.log("=".repeat(80));

    // Load business assets from database
    const assets = await loadBusinessAssets();

    if (assets.length === 0) {
      console.warn(
        "WARNING: No business assets loaded. Webhook will not process any events."
      );
    }

    // Start Express server
    app.listen(config.port, () => {
      console.log("\n" + "=".repeat(80));
      console.log("Facebook Webhook Server Started");
      console.log("=".repeat(80));
      console.log(`Port: ${config.port}`);
      console.log(`Webhook URL: http://localhost:${config.port}/webhook`);
      console.log(`Health Check: http://localhost:${config.port}/health`);
      console.log(`Reload Assets: http://localhost:${config.port}/reload`);
      console.log(`Verify Token: ${config.verifyToken ? "Set" : "Not Set"}`);
      console.log(`Supabase: ${config.supabaseUrl ? "Connected" : "Not Connected"}`);
      console.log(`Business Assets: ${assets.length} loaded`);
      console.log("=".repeat(80) + "\n");
      console.log("Listening for Facebook webhook events...\n");
    });
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

// Start the server
startServer();
