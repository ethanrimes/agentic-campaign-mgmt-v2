import json
import os
import time
from google import genai
from google.genai import types

# --- Configuration ---

# NOTE: The model must be one that supports structured output,
# gemini-2.5-flash is excellent for this.
MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # seconds

# --- Structured Output Schema Definition ---

# This defines the exact JSON structure the model must return.
# We map the dictionary structure provided in the request to
# the google-genai SDK's types.Schema objects.
VERIFICATION_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "has_source_link_if_news": types.Schema(
            type=types.Type.BOOLEAN,
            description="For news events: does the post include source URL(s)? Omit if not a news event."
        ),
        "has_no_offensive_content": types.Schema(
            type=types.Type.BOOLEAN,
            description="True means NO offensive content found."
        ),
        "has_no_misinformation": types.Schema(
            type=types.Type.BOOLEAN,
            description="For news events: True means NO misinformation found. Omit if not a news event."
        ),
        "is_approved": types.Schema(
            type=types.Type.BOOLEAN,
            description="Overall approval: should this post be published?"
        ),
        "reasoning": types.Schema(
            type=types.Type.STRING,
            description="Detailed explanation of the verification decision."
        ),
        "issues_found": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
            description="List of specific issues found. Empty if no issues."
        )
    },
    # Ensure these keys are always present in the generated JSON
    required=["has_no_offensive_content", "is_approved", "reasoning", "issues_found"]
)


def verify_content(post_text: str):
    """
    Sends content to the Gemini API for structured verification using
    the defined schema and handles retries with exponential backoff.
    """
    try:
        # Initialize the client. The client automatically uses the
        # GEMINI_API_KEY environment variable if set.
        # Set apiKey="" if running in an environment that provides the key automatically.
        api_key = os.getenv("GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)

        # 1. Define the system's role for better instruction adherence
        system_prompt = (
            "You are a Content Verification Bot. Your task is to analyze the user-provided "
            "social media post and determine its suitability for publication based on the "
            "provided JSON schema. Evaluate for offensiveness, misinformation (if news), "
            "and overall approval. Always return a valid JSON object matching the schema."
        )

        # 2. Configure the request for JSON output
        config = types.GenerateContentConfig(
            # Enforce JSON output format
            response_mime_type="application/json",
            # Pass the structured schema
            response_schema=VERIFICATION_SCHEMA,
            # Pass the system instruction
            system_instruction=system_prompt,
        )

        print(f"--- Analyzing Post ---")
        print(f'"{post_text}"\n')

        # 3. Call the API with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                # The core API call, as suggested in the request structure
                response = client.models.generate_content(
                    model=MODEL,
                    contents=post_text,
                    config=config
                )

                # The response.text contains the raw JSON string
                json_string = response.text
                
                # Parse the JSON string into a Python dictionary
                verification_result = json.loads(json_string)

                return verification_result

            except (genai.errors.ResourceExhaustedError, genai.errors.ServiceUnavailableError) as e:
                # Handle transient errors with exponential backoff
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_DELAY * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise Exception("Max retries reached. Could not complete API request.") from e
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None

    except Exception as e:
        print(f"Failed to run the script: {e}")
        return None

# --- Example Usage ---

# Example 1: A potentially problematic post (misinformation/unverified news)
post_to_check_1 = (
    "BREAKING: The government has just announced that all property taxes are being waived "
    "starting next month! Source: my friend's Facebook post."
)

# Example 2: A clean, non-news post
post_to_check_2 = "Just finished knitting a new sweater for my cat. It's purple and surprisingly stylish!"

if __name__ == "__main__":
    
    # Analyze Post 1 (News Event)
    result_1 = verify_content(post_to_check_1)
    if result_1:
        print("\n--- Verification Result 1 (News Post) ---")
        print(json.dumps(result_1, indent=4))
    
    print("\n" + "="*50 + "\n")

    # Analyze Post 2 (General Content)
    result_2 = verify_content(post_to_check_2)
    if result_2:
        print("\n--- Verification Result 2 (General Post) ---")
        print(json.dumps(result_2, indent=4))