import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a seasoned financial analyst. "
    "For any stock requested, you must return:\n"
    "• A single‑sentence short summary of its outlook.\n"
    "• A paragraph‑length detailed explanation.\n"
    "Label them exactly as “Short summary:” and “Detailed explanation:”."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_stock", methods=["POST"])
def analyze_stock():
    stock = (request.json or {}).get("stock", "").strip() or "Unknown Stock"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Generate the required short summary and detailed explanation for {stock}."},
        ],
    )

    text = response.choices[0].message.content.strip()

    # quick‑and‑dirty parsing
    short, detail = "No short summary found.", "No detailed explanation found."
    if "Short summary:" in text and "Detailed explanation:" in text:
        short, detail = text.split("Detailed explanation:", 1)
        short = short.replace("Short summary:", "").strip()
        detail = detail.strip()
    else:
        lines = text.splitlines()
        if lines:
            short, detail = lines[0].strip(), " ".join(lines[1:]).strip()

    return jsonify(short_summary=short, detailed_explanation=detail)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
