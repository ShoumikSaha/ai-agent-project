import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# ---------- OpenAI client ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- System prompt ----------
SYSTEM_PROMPT = (
    "You are a seasoned financial analyst. "
    "For any stock requested, you must return:\n"
    "• A single‑sentence short summary of its outlook.\n"
    "• A paragraph‑length detailed explanation.\n"
    "Label them exactly as “Short summary:” and “Detailed explanation:”."
)

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze_stock", methods=["POST"])
def analyze_stock():
    data = request.json or {}
    selected_stock = data.get("stock", "").strip() or "Unknown Stock"

    user_prompt = (
        f"Generate the required short summary and detailed explanation for {selected_stock}."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        ai_text = response.choices[0].message.content.strip()

        # ---- Parse model output ----
        short_summary = "No short summary found."
        detailed_explanation = "No detailed explanation found."

        if "Short summary:" in ai_text and "Detailed explanation:" in ai_text:
            summary_part, detail_part = ai_text.split("Detailed explanation:", 1)
            short_summary = summary_part.replace("Short summary:", "").strip()
            detailed_explanation = detail_part.strip()
        else:
            lines = ai_text.splitlines()
            if lines:
                short_summary = lines[0].strip()
                detailed_explanation = " ".join(lines[1:]).strip()

        return jsonify(
            short_summary=short_summary,
            detailed_explanation=detailed_explanation,
        )

    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    # Local dev; Render uses gunicorn via Procfile
    app.run(host="0.0.0.0", port=5000)
