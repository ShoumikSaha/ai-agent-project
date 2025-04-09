import os, json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a seasoned financial analyst. For any stock to be analyzed, "
    "you use these four indicators: Relative Strength Index (RSI), "
    "Exponential Moving Average (EMA), Moving Average Convergence Divergence (MACD), "
    "and Volume. You fetch the necessary data about these indicators before analyzing "
    "and making any decision. "
    'ALWAYS reply in valid JSON **only**, with the following structure:\n'
    '{\n'
    '  "Decision": {\n'
    '    "Buy":  "##%",\n'
    '    "Sell": "##%",\n'
    '    "Hold": "##%"\n'
    '  },\n'
    '  "Explanation": "string (may include **markdown bold**)"\n'
    '}\n'
    "Do not add any extra keys, comments, or text outside the JSON object."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_stock", methods=["POST"])
def analyze_stock():
    stock = (request.json or {}).get("stock", "").strip() or "Unknown Stock"

    USER_PROMPT = (
        f"First, analyze the stock {stock} in the current situation. "
        "Then provide the decision percentages (Buy / Sell / Hold) as described. "
        "After that, include a detailed explanation. "
        "Remember to output strictly the JSON object described above—nothing else."
    )

    # ---- OpenAI call -----------------------------------------------------
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT},
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    # ---- Robust JSON extraction -----------------------------------------
    # The model might wrap JSON in markdown fences; strip them if present.
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")              # remove back‑ticks
        first_brace = raw_text.find("{")
        raw_text = raw_text[first_brace : raw_text.rfind("}") + 1]

    try:
        obj = json.loads(raw_text)
    except json.JSONDecodeError:
        # fallback: return raw text so the UI shows something
        return jsonify(
            decision="(Could not parse JSON)\n" + raw_text,
            explanation=""
        )

    decision_dict = obj.get("Decision", {})
    decision_str  = ", ".join(f"{k}: {v}" for k, v in decision_dict.items())
    explanation   = obj.get("Explanation", "")

    return jsonify(
        decision=decision_str,
        explanation=explanation,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
