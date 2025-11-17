#!/usr/bin/env python3
"""
Migrate content_seed_id values in completed_posts to correct seed IDs.

This script updates the content_seed_id column to point to the correct seed
before the schema migration splits it into three foreign key columns.

Usage:
    python scripts/migrate_content_seed_ids.py
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mapping of incorrect content_seed_id values to correct seed IDs
# Format: {post_id: (correct_seed_id, seed_type)}
SEED_MAPPINGS = {
    # News Event Seeds
    # SEPTA Fare Increase (bc100172-f892-4d50-8fc6-86b3a2a2e378)
    "14ae715c-892f-49e6-ba2a-d406a59f96ff": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "19325956-ca48-4d9f-9583-179053903f31": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "2d5316ed-93a0-42ba-9bd4-b4bb84333901": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "52f6191e-d72a-4485-9ffd-fb0f7e999193": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "728fd650-a793-4c88-b5e6-65582af2fa62": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "79afb418-2757-4f85-87f8-2a1c6792fe70": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "8e8f572c-58e3-461b-b9a7-df50f05d5ee8": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "a15e6b94-4503-46df-a8a5-2a07e3e71153": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "a71ff615-2541-477c-ac49-2dfec9ec51ba": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "dd157ff4-e25d-4cf8-8e94-b5b835d16027": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),
    "f37660ea-c79e-448b-bd4f-7ecb80032604": ("bc100172-f892-4d50-8fc6-86b3a2a2e378", "news_event"),

    # Philadelphia Marathon 2025 (50423190-0a07-4abe-a095-b36987068a8c)
    "18324a6a-8b6c-487a-8408-7a32fe952dd2": ("50423190-0a07-4abe-a095-b36987068a8c", "news_event"),
    "a2c2a637-34ba-407c-a203-8fee1f5a3473": ("50423190-0a07-4abe-a095-b36987068a8c", "news_event"),
    "b1379a95-270a-4a40-90de-7fcac20827a3": ("50423190-0a07-4abe-a095-b36987068a8c", "news_event"),

    # Flesh and Blood TCG World Championship 2025 (939b1c53-4128-4bde-9456-27fe68e3e6cc)
    "aff974ea-e428-4816-99d9-30acb1c5ee96": ("939b1c53-4128-4bde-9456-27fe68e3e6cc", "news_event"),
    "fa49db8c-9bb4-4747-93b4-84a39163fcc8": ("939b1c53-4128-4bde-9456-27fe68e3e6cc", "news_event"),

    # Trend Seeds
    # Penn Picks: Study + Eats Micro-Guides (644edf6d-7de3-4d5b-9027-721003ec4df3)
    "02219eba-22ec-4cce-be29-b9021d27a49b": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "111bd67e-75e1-4590-857a-354d0cf29ac9": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "3b622831-784f-4dca-b39c-e0dcc0cf7f2d": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "4569ae88-4b29-4b57-a024-880c09f539ea": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "5d20d8b9-e558-4bff-b018-83c056eea3d2": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "6950b2ac-cd5b-4d2a-bb87-29cc51d8e856": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "79e4dd56-46fa-42e2-9d35-cd096b8ece45": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "89d361c7-d3d6-47cd-b967-d563ee36bbe0": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "e15bd50e-ce95-43a7-8e1d-6703a8f365c4": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "e5471d86-f48c-473a-98fa-e36d9a2be774": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),
    "fe0b1f8c-3fc7-4adb-a9c8-674d23d1382d": ("644edf6d-7de3-4d5b-9027-721003ec4df3", "trend"),

    # Penn Campus Winter Aesthetic (4743f89d-3407-47ba-8866-e0e086dd624b)
    "02d59d2f-4600-4f0a-8ec5-285084f499b0": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "36f51dbf-1d0c-4785-b275-6ccc25aebdd0": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "4cf80716-8b74-4835-ad5c-281ca9becbb5": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "4dd8e52b-a580-468a-b7bc-3404a6a05baa": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "62112d26-0f46-4ad8-ba2a-20d14a5d5d9d": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "89386dd6-c859-4dd3-90c4-6a35abce0263": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "8f3035e3-87cd-465f-9a5e-9f9decc3ae7f": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "97a9e148-1711-46f3-a5fa-ec6a5dad219b": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "a1badb72-fcdf-4ca5-88dd-30f002e9ff54": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "abcdb432-7e92-4fc1-b34f-79730d3a3050": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "bca2ccc3-0659-48a1-b78c-9ca1e695dd82": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "d95522d7-e32b-4426-97ec-4ace1fd8ca75": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "e9730852-3365-46be-88a2-1ce035b72778": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "ed979fca-bc7a-4fd4-9cbc-d234ba5174dc": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),
    "f1acb421-11ba-44fa-8c65-27316eca2d3b": ("4743f89d-3407-47ba-8866-e0e086dd624b", "trend"),

    # Penn Campus Micro-Utility (90d2dcb9-2ee4-48ed-ad91-60520a57d74e)
    "186f1121-c08f-49f3-8546-ae8223fc9e08": ("90d2dcb9-2ee4-48ed-ad91-60520a57d74e", "trend"),
    "712bc6a4-2c94-4c72-a589-3cac1c6ea4e0": ("90d2dcb9-2ee4-48ed-ad91-60520a57d74e", "trend"),
    "909cec70-fd79-473a-80a8-af5ee01c2448": ("90d2dcb9-2ee4-48ed-ad91-60520a57d74e", "trend"),
    "b72650a3-0392-4385-acd9-4101ba41afb2": ("90d2dcb9-2ee4-48ed-ad91-60520a57d74e", "trend"),

    # Penn Campus Aesthetic Reels (141ccc84-6dea-4028-a63a-8f0a4fa86198)
    "1b44094a-7a11-4996-a006-de28d86ae19e": ("141ccc84-6dea-4028-a63a-8f0a4fa86198", "trend"),
    "2cb51328-e7b9-4674-b1d4-4397b5689671": ("141ccc84-6dea-4028-a63a-8f0a4fa86198", "trend"),
    "99754290-39f2-499a-96e2-aadcf5b5f13e": ("141ccc84-6dea-4028-a63a-8f0a4fa86198", "trend"),

    # Ungrounded Seeds
    # Study spot recommendations (5da09533-5ce3-4d93-9a0c-a9095187ded0)
    "0378dbc8-4b17-416c-8d24-cd436486397d": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "05889977-baf4-4604-ae16-7f7e4bfa9093": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "392fbf46-74a1-4b0c-bb17-d3d4a251c4b0": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "39b9c1f9-d668-4cfe-801f-0af447703d20": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "3edcd772-531e-4cfe-a785-3bdbb765a19f": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "66f9d553-caa2-4945-8987-7361d543f080": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "92c247fb-e62a-496d-814d-9d4e7bd91fe2": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "94f96046-5b25-420c-aaff-d29146821c11": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "a057712e-5223-4836-be34-4df3de343e1b": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "b682aeef-d68b-41ea-83f0-a448e9ca3966": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "cc125385-a1f8-427f-a124-ba5003c2a64b": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),
    "d66d18b1-6a8f-49bf-9753-4357acb6dbce": ("5da09533-5ce3-4d93-9a0c-a9095187ded0", "ungrounded"),

    # Penn Passport (4ecfee6d-a62a-4dda-9b73-5ceefb41a086)
    "47588d8a-ee9d-416f-8fc4-8dd0e0bc17c3": ("4ecfee6d-a62a-4dda-9b73-5ceefb41a086", "ungrounded"),
    "4f148ee1-4cc0-44e5-a8ae-5e1afbe808fb": ("4ecfee6d-a62a-4dda-9b73-5ceefb41a086", "ungrounded"),
    "868f1d42-340c-45c7-aa28-d2b28ea962e2": ("4ecfee6d-a62a-4dda-9b73-5ceefb41a086", "ungrounded"),
    "c31326d3-80b9-4d7a-b806-90474a20bdf2": ("4ecfee6d-a62a-4dda-9b73-5ceefb41a086", "ungrounded"),
    "ec8eac7f-b766-46e7-a442-778927316b13": ("4ecfee6d-a62a-4dda-9b73-5ceefb41a086", "ungrounded"),

    # Culinary Traditions at Penn (fcca0f20-565e-4eff-b9d2-4c5da3e0f13c)
    "b4546362-737d-4ab9-b27a-dff10f870d02": ("fcca0f20-565e-4eff-b9d2-4c5da3e0f13c", "ungrounded"),
    "f66669e2-6537-4e24-90b0-1ee36d0feebb": ("fcca0f20-565e-4eff-b9d2-4c5da3e0f13c", "ungrounded"),
    "f6d41363-f8a2-48f5-81f7-2da4d59092aa": ("fcca0f20-565e-4eff-b9d2-4c5da3e0f13c", "ungrounded"),

    # Penn Micro-Adventures (a6bc2231-8d03-4155-bd6d-6f4c42a723d8)
    "b5b14f0f-b080-4e62-bba2-921e0285e033": ("a6bc2231-8d03-4155-bd6d-6f4c42a723d8", "ungrounded"),
    "deca90f4-cfb5-49d8-ae8d-542a3bae09aa": ("a6bc2231-8d03-4155-bd6d-6f4c42a723d8", "ungrounded"),
}


def get_db_connection():
    """Get database connection."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set in environment")
        sys.exit(1)
    return psycopg2.connect(db_url)


def migrate_content_seed_ids():
    """Migrate content_seed_id values to correct seed IDs."""
    print("🔄 Migrating content_seed_id values...\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # First, get a count of posts that need migration
        cursor.execute("""
            SELECT COUNT(*) FROM completed_posts
            WHERE id::text = ANY(%s)
        """, (list(SEED_MAPPINGS.keys()),))

        count = cursor.fetchone()[0]
        print(f"Found {count} posts that need content_seed_id migration")

        if count == 0:
            print("✅ No posts need migration")
            return

        # Migrate each post (commit each one individually)
        migrated = 0
        failed = 0

        for post_id, (seed_id, seed_type) in SEED_MAPPINGS.items():
            try:
                cursor.execute("""
                    UPDATE completed_posts
                    SET content_seed_id = %s,
                        content_seed_type = %s
                    WHERE id = %s
                """, (seed_id, seed_type, post_id))

                conn.commit()  # Commit each update individually

                if cursor.rowcount > 0:
                    migrated += 1
                    print(f"  ✅ Migrated post {post_id[:8]}... to seed {seed_id[:8]}... ({seed_type})")

            except Exception as e:
                conn.rollback()  # Rollback failed transaction
                failed += 1
                print(f"  ❌ Failed to migrate post {post_id[:8]}...: {e}")
        print(f"\n✅ Migration complete: {migrated} posts migrated, {failed} failed")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    migrate_content_seed_ids()
