import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Google Gemini API Test")
print("=" * 60)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

print(f"\nAPI Key configured: {'Yes' if api_key else 'No'}")
if api_key and api_key != "your-gemini-api-key-here":
    print(f"API Key (first 15 chars): {api_key[:15]}...")
else:
    print("\n❌ Please set your GEMINI_API_KEY in the .env file")
    print("\nGet your free API key from: https://aistudio.google.com/app/apikey")
    exit(1)

print(f"Model: {model_name}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    print(f"\nSending request to Gemini...")
    
    response = model.generate_content("What is 2+2? Answer with just the number.")
    
    print(f"\n✅ SUCCESS!")
    print(f"Response: {response.text}")
    
    # Test with financial question
    print("\n" + "=" * 60)
    print("Testing Financial Analysis")
    print("=" * 60)
    
    financial_response = model.generate_content(
        "Explain in one sentence why cash flow is important for businesses."
    )
    print(f"\nResponse: {financial_response.text}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
