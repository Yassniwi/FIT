import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import MODEL_NAME, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Please enter a message."}), 400

    contents = []
    for item in history:
        role = "user" if item.get("role") == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=item.get("text", ""))])
        )
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.6,
            ),
        )
        return jsonify({"reply": response.text})
    except Exception as error:
        return jsonify({"error": f"Something went wrong: {error}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
