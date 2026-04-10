import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types # 1. Added this import

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. SETUP & DATA LOADING
df = pd.read_csv("src/data/cleaned_dataset.csv").head(50) # Keep .head(50) for pilot
df = df.drop(columns=['genre_id', 'tempo_normalized', 'loudness_normalized', 'mood_score', 'transition_score'])

# 2. THE PROMPT BUILDER
def build_prompt(row):
    return f"""You are a music mood labeling system.
Assign a score from 0 to 1 for each mood. Each mood is independent.
...
Song data:
- Track: {row['track_name']} by {row['artists']}
- Energy: {row['energy']}, Valence: {row['valence']}
...
Return ONLY JSON:
{{
  "calm": 0.0, "happy": 0.0, "energetic": 0.0, "sad": 0.0,
  "dark": 0.0, "romantic": 0.0, "focus": 0.0, "hype": 0.0
}}"""

# 3. GENERATE THE JSONL FILE
BATCH_FILE_PATH = "src/data/music_batch_requests.jsonl"

print(f"Generating request file for {len(df)} tracks...")
with open(BATCH_FILE_PATH, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        # NOTE: Using 'key' instead of 'custom_id' for AI Studio Batch API
        request_line = {
            "key": str(row['track_id']), 
            "request": {
                "model": "models/gemini-2.5-flash-lite",
                "contents": [{"role": "user", "parts": [{"text": build_prompt(row)}]}],
                "generation_config": {
                    "temperature": 0,
                    "response_mime_type": "application/json",
                }
            }
        }
        f.write(json.dumps(request_line) + "\n")

# 4. UPLOAD AND SUBMIT
print("Uploading to Google Cloud...")
# FIX: Added config with mime_type
uploaded_file = client.files.upload(
    file=BATCH_FILE_PATH,
    config=types.UploadFileConfig(
        mime_type='application/json'
    )
)

print("Starting Batch Job...")
batch_job = client.batches.create(
    model="gemini-2.5-flash-lite",
    src=uploaded_file.name,
    config={"display_name": f"Pilot_Labeling_{len(df)}_tracks"}
)

print("-" * 30)
print(f"SUCCESS: Batch Job Created!")
print(f"Job ID: {batch_job.name}")
print("-" * 30)