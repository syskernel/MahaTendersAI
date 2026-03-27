from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def analyze_title(title):
    prompt = f"""describe {title}. Final output should look like:
        job: (description in 6-7 words)
        tiles/stones: (yes/no)"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview", contents=prompt
    )

    data = response.text.strip()

    job = ""
    tiles = ""
    for line in data.split("\n"):
        if line.lower().startswith("job:"):
            job = line.split(":",1)[1].strip()
        if line.lower().startswith("tiles/stones:"):
            tiles = line.split(":",1)[1].strip()

    return job, tiles

def contact_info(name):
    pass