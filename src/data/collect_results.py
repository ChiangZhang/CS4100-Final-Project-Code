import json
import pandas as pd
import os
from google import genai
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# IMPORTANT: You get this name from your check_status.py output 
# It usually looks like 'files/xxxxxxxxxxxx'
OUTPUT_FILE_NAME = "PASTE_OUTPUT_FILE_NAME_HERE" 

# File paths
LOCAL_RESULTS_PATH = "src/data/batch_results.jsonl"
ORIGINAL_DATA_PATH = "src/data/cleaned_dataset.csv"
FINAL_OUTPUT_PATH = "src/data/cleaned_labeled_dataset.csv"

def collect():
    # 2. DOWNLOAD THE FILE FROM GOOGLE
    # This grabs the JSONL file Gemini created and saves it to your computer
    print(f"Downloading {OUTPUT_FILE_NAME}...")
    try:
        # Some SDK versions use 'file' or 'name', 'name' is standard here
        client.files.download(name=OUTPUT_FILE_NAME, path=LOCAL_RESULTS_PATH)
        print("Download successful.")
    except Exception as e:
        print(f"Download failed: {e}")
        return

    # 3. PARSE THE JSONL AND EXTRACT MOODS
    print("Parsing results and matching with Track IDs...")
    results = []
    with open(LOCAL_RESULTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            
            # The 'key' we set in label_dataset.py is our track_id
            track_id = entry.get('key')
            
            try:
                # Navigate the nested Gemini response structure
                # response -> candidates -> content -> parts -> text
                raw_ai_text = entry['response']['candidates'][0]['content']['parts'][0]['text']
                
                # Convert that string back into a Python dictionary
                mood_scores = json.loads(raw_ai_text)
                
                # Add the track_id back in so we can merge
                mood_scores['track_id'] = track_id
                results.append(mood_scores)
            except (KeyError, json.JSONDecodeError) as e:
                print(f"Skipping a result due to formatting error: {e}")

    # 4. MERGE WITH YOUR ORIGINAL FEATURES
    print("Merging with original dataset...")
    labels_df = pd.DataFrame(results)
    original_df = pd.read_csv(ORIGINAL_DATA_PATH)

    # This combines the 9 audio features with the 8 new mood probabilities
    final_df = pd.merge(original_df, labels_df, on="track_id")

    # 5. SAVE THE FINAL TRAINING DATA
    final_df.to_csv(FINAL_OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print(f"SUCCESS: Created {FINAL_OUTPUT_PATH}")
    print(f"Total songs labeled and merged: {len(final_df)}")
    print("-" * 30)
    print(final_df[['track_name', 'happy', 'calm', 'energetic', 'dark']].head())

if __name__ == "__main__":
    collect()