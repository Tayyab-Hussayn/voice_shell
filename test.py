from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {api_key[:10]}...{api_key[-5:] if api_key else 'NONE'}")

# Initialize client
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Say hello'
    )
    print("✅ SUCCESS!")
    print(response.text)
except Exception as e:
    print(f"❌ ERROR: {e}")
