import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("\nAvailable Gemini Models:\n")

    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(model.name)

except Exception as e:
    print(f"Error: {e}")