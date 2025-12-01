import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(API_KEY)}")
if API_KEY:
    print(f"API Key starts with: {API_KEY[:5]}...")

genai.configure(api_key=API_KEY)

try:
    print("Testing gemini-2.0-flash-lite-001...")
    model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
    response = model.generate_content("Hello")
    print("Response received:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
