import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Your specific Job ID from the terminal
JOB_ID = "batches/mnq18e76ifz9qd1en00204vunmk56ng0jaqx"

def check():
    job = client.batches.get(name=JOB_ID)
    print(f"Job ID: {job.name}")
    print(f"Status: {job.state}") # Look for 'SUCCEEDED'
    
    if job.state == "SUCCEEDED":
        print("-" * 30)
        print("COMPLETED!")
        print(f"Output File Name: {job.output_file_name}")
        print("-" * 30)
        print("You can now run collect_results.py")
    elif job.state == "FAILED":
        print(f"Error: {job.error}")

if __name__ == "__main__":
    check()