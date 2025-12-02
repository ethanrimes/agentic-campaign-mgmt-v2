from google import genai
from google.genai import types
import os

# --- File Paths ---
video_file_name = "/Users/ethan/Downloads/20251125_021220_ad21799d.mp4"
image_file_name = "/Users/ethan/Downloads/20251112_045312_a8d54325.png"

# --- Read Data ---
try:
    # Read video data
    with open(video_file_name, 'rb') as f:
        video_bytes = f.read()

    # Read image data
    with open(image_file_name, 'rb') as f:
        image_bytes = f.read()
        
except FileNotFoundError as e:
    print(f"Error: File not found. Please check the path: {e.filename}")
    exit()

# --- Gemini API Call ---
client = genai.Client()

print("Sending video and image data for analysis...")

# Note on Inline Data: The total size of all inline data (video + image + text)
# in this request must be kept under the API's limit (typically <20MB).

response = client.models.generate_content(
    model='models/gemini-2.5-flash',
    contents=types.Content(
        parts=[
            # 1. Video Input Part
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            # 2. Image Input Part (New)
            types.Part(
                # Use the correct MIME type for PNG
                inline_data=types.Blob(data=image_bytes, mime_type='image/png') 
            ),
            # 3. Text Prompt
            types.Part(text='Please summarize  describe the photo in three sentences total, combining the information.')
        ]
    )
)

print("\n--- Model Response ---")
print(response.text)