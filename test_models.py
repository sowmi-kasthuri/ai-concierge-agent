import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# List available models
models = genai.list_models()

for m in models:
    print(m.name)
