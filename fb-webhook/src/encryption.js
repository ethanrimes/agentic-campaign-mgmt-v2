// fb-webhook/src/encryption.js

/**
 * Encryption/decryption utilities using Fernet-compatible encryption.
 *
 * Fernet uses AES-128-CBC with HMAC-SHA256 for authentication.
 * The format is: base64(version || timestamp || iv || ciphertext || hmac)
 */

const crypto = require("crypto");

/**
 * Decrypt a Fernet-encrypted token.
 *
 * @param {string} encryptedToken - Base64-encoded Fernet token
 * @param {string} key - Base64-encoded Fernet key (32 bytes: 16 for signing, 16 for encryption)
 * @returns {string} Decrypted plaintext
 * @throws {Error} If decryption fails
 */
function decryptFernetToken(encryptedToken, key) {
  try {
    // Decode the key (Fernet key is base64 URL-safe encoded, 32 bytes)
    const keyBuffer = Buffer.from(key, "base64");

    if (keyBuffer.length !== 32) {
      throw new Error(`Invalid key length: ${keyBuffer.length} (expected 32)`);
    }

    // Split key into signing key and encryption key
    const signingKey = keyBuffer.slice(0, 16);
    const encryptionKey = keyBuffer.slice(16, 32);

    // Decode the token
    const tokenBuffer = Buffer.from(encryptedToken, "base64");

    // Parse Fernet token structure:
    // version (1 byte) || timestamp (8 bytes) || iv (16 bytes) || ciphertext || hmac (32 bytes)
    const version = tokenBuffer[0];
    if (version !== 0x80) {
      throw new Error(`Unsupported Fernet version: ${version}`);
    }

    const timestamp = tokenBuffer.slice(1, 9);
    const iv = tokenBuffer.slice(9, 25);
    const ciphertext = tokenBuffer.slice(25, -32);
    const hmac = tokenBuffer.slice(-32);

    // Verify HMAC
    const dataToVerify = tokenBuffer.slice(0, -32);
    const expectedHmac = crypto
      .createHmac("sha256", signingKey)
      .update(dataToVerify)
      .digest();

    if (!crypto.timingSafeEqual(hmac, expectedHmac)) {
      throw new Error("HMAC verification failed");
    }

    // Decrypt using AES-128-CBC
    const decipher = crypto.createDecipheriv("aes-128-cbc", encryptionKey, iv);
    let decrypted = decipher.update(ciphertext);
    decrypted = Buffer.concat([decrypted, decipher.final()]);

    return decrypted.toString("utf8");
  } catch (error) {
    throw new Error(`Fernet decryption failed: ${error.message}`);
  }
}

module.exports = {
  decryptFernetToken,
};
