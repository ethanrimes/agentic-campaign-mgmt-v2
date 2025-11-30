// fb-webhook/src/businessAssets.js

/**
 * Business Assets Manager
 *
 * Loads and manages business assets from the Supabase database.
 * Provides lookup by Facebook page ID and caches decrypted credentials.
 */

const { createClient } = require("@supabase/supabase-js");
const { config } = require("./config");
const { decryptFernetToken } = require("./encryption");

// In-memory cache for business assets
let businessAssets = [];
let pageIdToAssetMap = new Map();
let supabase = null;

/**
 * Initialize the Supabase client.
 */
function initializeSupabase() {
  if (!supabase) {
    supabase = createClient(config.supabaseUrl, config.supabaseServiceKey);
  }
  return supabase;
}

/**
 * Load all active business assets from the database and cache them.
 *
 * @returns {Promise<Array>} Array of business assets with decrypted credentials
 */
async function loadBusinessAssets() {
  const client = initializeSupabase();

  console.log("Loading business assets from database...");

  const { data, error } = await client
    .from("business_assets")
    .select("*")
    .eq("is_active", true);

  if (error) {
    throw new Error(`Failed to load business assets: ${error.message}`);
  }

  if (!data || data.length === 0) {
    console.warn("No active business assets found in database");
    businessAssets = [];
    pageIdToAssetMap.clear();
    return businessAssets;
  }

  console.log(`Found ${data.length} active business assets`);

  // Process and cache business assets
  businessAssets = data.map((asset) => {
    // Decrypt access tokens
    let facebookAccessToken = null;
    let instagramAccessToken = null;

    try {
      facebookAccessToken = decryptFernetToken(
        asset.facebook_page_access_token_encrypted,
        config.encryptionKey
      );
    } catch (err) {
      console.error(
        `Failed to decrypt Facebook token for ${asset.id}:`,
        err.message
      );
    }

    try {
      instagramAccessToken = decryptFernetToken(
        asset.instagram_page_access_token_encrypted,
        config.encryptionKey
      );
    } catch (err) {
      console.error(
        `Failed to decrypt Instagram token for ${asset.id}:`,
        err.message
      );
    }

    return {
      id: asset.id,
      name: asset.name,
      facebookPageId: asset.facebook_page_id,
      instagramAccountId: asset.app_users_instagram_account_id,
      facebookAccessToken,
      instagramAccessToken,
      targetAudience: asset.target_audience,
      isActive: asset.is_active,
    };
  });

  // Build lookup map by Facebook page ID
  pageIdToAssetMap.clear();
  for (const asset of businessAssets) {
    if (asset.facebookPageId) {
      pageIdToAssetMap.set(asset.facebookPageId, asset);
      console.log(
        `  - ${asset.name} (${asset.id}): Facebook Page ID = ${asset.facebookPageId}`
      );
    }
  }

  console.log(
    `Loaded ${businessAssets.length} business assets with ${pageIdToAssetMap.size} Facebook page mappings`
  );

  return businessAssets;
}

/**
 * Get a business asset by its Facebook page ID.
 *
 * @param {string} facebookPageId - The Facebook page ID
 * @returns {Object|null} Business asset or null if not found
 */
function getAssetByFacebookPageId(facebookPageId) {
  return pageIdToAssetMap.get(facebookPageId) || null;
}

/**
 * Get a business asset by its ID.
 *
 * @param {string} assetId - The business asset ID
 * @returns {Object|null} Business asset or null if not found
 */
function getAssetById(assetId) {
  return businessAssets.find((asset) => asset.id === assetId) || null;
}

/**
 * Get all loaded business assets.
 *
 * @returns {Array} Array of business assets
 */
function getAllAssets() {
  return businessAssets;
}

/**
 * Get the Supabase client instance.
 *
 * @returns {Object} Supabase client
 */
function getSupabaseClient() {
  return initializeSupabase();
}

/**
 * Reload business assets from the database.
 * Call this periodically or after credential updates.
 *
 * @returns {Promise<Array>} Updated array of business assets
 */
async function reloadBusinessAssets() {
  console.log("Reloading business assets...");
  return await loadBusinessAssets();
}

module.exports = {
  loadBusinessAssets,
  reloadBusinessAssets,
  getAssetByFacebookPageId,
  getAssetById,
  getAllAssets,
  getSupabaseClient,
};
