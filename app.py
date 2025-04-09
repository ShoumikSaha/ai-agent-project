import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    website = data.get("website", "")
    if not website:
        return jsonify({"error": "No website provided"}), 400

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that comments on websites."},
                {"role": "user", "content": f"Provide a short, helpful response about the website: {website}"}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        text = completion.choices[0].message.content.strip()
        return jsonify({"response": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))