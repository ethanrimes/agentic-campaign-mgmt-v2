// fb-webhook/src/config.js

/**
 * Configuration module for the Facebook webhook server.
 * Validates and exports all environment variables.
 */

require("dotenv").config({ path: process.env.ENV_FILE_PATH || "../.env" });

const config = {
  // Server configuration
  port: parseInt(process.env.WEBHOOK_PORT || process.env.PORT || "3000", 10),

  // Webhook verification
  verifyToken: process.env.FACEBOOK_WEBHOOK_VERIFY_TOKEN,

  // Supabase connection
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseServiceKey: process.env.SUPABASE_SERVICE_KEY,

  // Encryption key for Fernet decryption
  encryptionKey: process.env.ENCRYPTION_KEY,

  // Meta App credentials (for API requests)
  metaAppId: process.env.META_APP_ID,
  metaAppSecret: process.env.META_APP_SECRET,
};

/**
 * Validate that all required environment variables are set.
 * @throws {Error} If any required variable is missing
 */
function validateConfig() {
  const required = [
    ["FACEBOOK_WEBHOOK_VERIFY_TOKEN", config.verifyToken],
    ["SUPABASE_URL", config.supabaseUrl],
    ["SUPABASE_SERVICE_KEY", config.supabaseServiceKey],
    ["ENCRYPTION_KEY", config.encryptionKey],
  ];

  const missing = required.filter(([name, value]) => !value);

  if (missing.length > 0) {
    const names = missing.map(([name]) => name).join(", ");
    console.error(`ERROR: Missing required environment variables: ${names}`);
    process.exit(1);
  }
}

module.exports = {
  config,
  validateConfig,
};
