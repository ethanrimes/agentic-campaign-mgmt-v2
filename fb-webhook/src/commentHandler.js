// fb-webhook/src/commentHandler.js

/**
 * Comment Event Handler
 *
 * Processes Facebook comment webhook events, fetches additional details
 * from the Graph API, and stores comments in the database.
 */

const {
  getAssetByFacebookPageId,
  getSupabaseClient,
} = require("./businessAssets");

/**
 * Fetch full comment details from the Facebook Graph API.
 *
 * @param {string} commentId - The comment ID
 * @param {string} accessToken - Page access token
 * @returns {Promise<Object>} Comment details from the API
 */
async function fetchCommentDetails(commentId, accessToken) {
  const url = `https://graph.facebook.com/v24.0/${commentId}`;
  const params = new URLSearchParams({
    fields:
      "message,from,created_time,parent,permalink_url,comment_count,like_count,attachment",
    access_token: accessToken,
  });

  console.log(`Fetching comment details for: ${commentId}`);

  const response = await fetch(`${url}?${params}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Facebook API error: ${response.status} ${response.statusText} - ${errorText}`
    );
  }

  return await response.json();
}

/**
 * Handle a Facebook comment event from the webhook.
 *
 * @param {Object} value - The change.value object from the webhook payload
 * @param {string} pageId - The Facebook page ID (from entry.id)
 */
async function handleCommentEvent(value, pageId) {
  try {
    console.log("\nHandling comment event:");
    console.log(JSON.stringify(value, null, 2));

    const commentId = value.comment_id;
    const postId = value.post_id;
    const verb = value.verb; // "add", "edit", or "remove"

    // Only process new comments (verb = "add")
    if (verb !== "add") {
      console.log(`Skipping comment with verb: ${verb}`);
      return;
    }

    // Find the business asset for this page
    const businessAsset = getAssetByFacebookPageId(pageId);

    if (!businessAsset) {
      console.error(`No business asset found for Facebook page ID: ${pageId}`);
      return;
    }

    console.log(
      `Matched to business asset: ${businessAsset.name} (${businessAsset.id})`
    );

    // Check if we have a valid access token
    if (!businessAsset.facebookAccessToken) {
      console.error(
        `No Facebook access token for business asset: ${businessAsset.id}`
      );
      return;
    }

    // Fetch full comment details from Facebook Graph API
    const commentDetails = await fetchCommentDetails(
      commentId,
      businessAsset.facebookAccessToken
    );

    console.log("\nFetched comment details:");
    console.log(JSON.stringify(commentDetails, null, 2));

    const commentText = commentDetails.message || "";

    // Skip comments without text (reactions, media-only, stickers, etc.)
    if (!commentText.trim()) {
      console.log(`Skipping comment without text (comment_id: ${commentId})`);
      return;
    }

    // Extract commenter info from API response
    const from = commentDetails.from || {};
    const commenterName = from.name || "Unknown";
    const commenterId = from.id || "unknown";

    // Skip comments from our own Page (prevents responding to our own replies)
    if (commenterId === pageId) {
      console.log(`Skipping comment from own Page (comment_id: ${commentId}, commenter_id: ${commenterId})`);
      return;
    }

    // Extract parent_id if this is a reply
    const parentId = commentDetails.parent?.id || value.parent_id || null;

    // Extract timestamp from API response
    const createdTime = commentDetails.created_time
      ? new Date(commentDetails.created_time).toISOString()
      : new Date().toISOString();

    // Prepare comment data for database
    const commentData = {
      platform: "facebook",
      comment_id: commentId,
      post_id: postId,
      comment_text: commentText,
      commenter_username: commenterName,
      commenter_id: commenterId,
      parent_comment_id: parentId,
      created_time: createdTime,
      like_count: commentDetails.like_count || 0,
      permalink_url: commentDetails.permalink_url || null,
      status: "pending",
      business_asset_id: businessAsset.id,
    };

    console.log("\nInserting comment to database:");
    console.log(JSON.stringify(commentData, null, 2));

    // Insert into Supabase
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from("platform_comments")
      .insert(commentData)
      .select();

    if (error) {
      // Check if it's a duplicate (comment_id already exists)
      if (error.code === "23505") {
        // Unique violation
        console.log(`Comment ${commentId} already exists in database, skipping`);
        return;
      }

      throw error;
    }

    console.log(`\n Successfully saved comment to database`);
    console.log(`  Database ID: ${data[0]?.id}`);
    console.log(`  Comment ID: ${commentId}`);
    console.log(`  Post ID: ${postId}`);
    console.log(`  Business Asset: ${businessAsset.id}`);
    console.log(`  Commenter: ${commenterName}`);
    console.log(
      `  Text: "${commentText.substring(0, 50)}${commentText.length > 50 ? "..." : ""}"`
    );
  } catch (error) {
    console.error("\nError handling comment event:");
    console.error(error);
  }
}

module.exports = {
  handleCommentEvent,
  fetchCommentDetails,
};
