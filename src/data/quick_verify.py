import pandas as pd
import json
import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. Load data
INPUT_PATH = "src/data/cleaned_dataset.csv"
OUTPUT_PATH = "src/data/validation_5k_labeled.csv"

# Verify file exists before starting
if not os.path.exists(INPUT_PATH):
    print(f"Error: Could not find {INPUT_PATH}")
    exit()

df = pd.read_csv(INPUT_PATH).head(500)

# 2. THE PROMPT BUILDER (Fully Defined)
def build_prompt(row):
    # Convert Mode to human-readable text for the LLM
    mode_text = "Major (Uplifting)" if row['mode'] == 1 else "Minor (Serious/Sad)"
    explicit_text = "Yes" if row['explicit'] else "No"
    
    return f"""You are a music mood labeling system. 
Assign scores (0-1) for 8 independent moods based on audio data.
Song data:
- Track: {row['track_name']} by {row['artists']}
- Energy: {row['energy']}, Valence: {row['valence']}

Return ONLY JSON:
{{
  "calm": 0.0, "happy": 0.0, "energetic": 0.0, "sad": 0.0,
  "dark": 0.0, "romantic": 0.0, "focus": 0.0, "hype": 0.0
}}"""

print(f"Starting labeling for 5,000 songs...")

# 3. CHECKPOINTING LOGIC
start_index = 0
if os.path.exists(OUTPUT_PATH):
    try:
        existing_df = pd.read_csv(OUTPUT_PATH)
        start_index = len(existing_df)
        print(f"Resuming from index {start_index}...")
    except:
        print("Starting fresh...")

# 4. THE LOOP
for i in range(start_index, len(df)):
    row = df.iloc[i]
    try:
        # Generate content
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=build_prompt(row), 
            config={
                "temperature": 0, 
                "response_mime_type": "application/json"
            }
        )
        
        # Parse result
        mood_data = json.loads(response.text)
        
        # Combine original row data with new labels
        combined_data = {**row.to_dict(), **mood_data}
        result_df = pd.DataFrame([combined_data])
        
        # Append to CSV
        result_df.to_csv(OUTPUT_PATH, mode='a', index=False, header=not os.path.exists(OUTPUT_PATH))
        
        # Print progress every 5 songs so you know it's alive
        if (i + 1) % 5 == 0:
            print(f"[{i+1}/5000] Successfully Labeled: {row['track_name']}")
            
    except Exception as e:
        print(f"Error on {row['track_name']}: {e}")
        time.sleep(2) # Short pause before next attempt

print(f"Done! Labeled data saved to {OUTPUT_PATH}")