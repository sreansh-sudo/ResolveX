import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")

# Function to handle chat
def get_ai_response(message, history=None):
    if history is None:
        history = []

    try:
        chat = model.start_chat(history=[
            {"role": msg["role"], "parts": [msg["content"]]} for msg in history
        ])
        response = chat.send_message(message)
        reply = response.text

        history.append({"role": "user", "content": message})
        history.append({"role": "model", "content": reply})

        return reply, history

    except Exception as e:
        return f"❌ Error talking to Gemini: {e}", history
