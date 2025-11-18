from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api = os.getenv("GEMINI_API_KEY")
if not api:
    print("API key missing")
    raise SystemExit

client = genai.Client(api_key=api)

try:
    resp = client.models.generate_content(
       model="models/gemini-2.0-flash",
       contents="Say 'model confirmed' if this works."
    )
    print(resp.text)
except Exception as e:
    print("Error:", e)
