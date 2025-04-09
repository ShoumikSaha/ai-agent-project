import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a seasoned financial analyst. For any stock to be analyzed, "
    "you use these four indicators: Relative Strength Index (RSI), "
    "Exponential Moving Average (EMA), Moving Average Convergence "
    "Divergence (MACD), and Volume. You fetch the necessary data about "
    "these indicators before analyzing and making any decision. "
    'For any stock, you provide 2 things: the decision and the explanation. '
    'Label them exactly as "Decision:" and "Explanation:".'
)

# ── Routes ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze_stock", methods=["POST"])
def analyze_stock():
    stock = (request.json or {}).get("stock", "").strip() or "Unknown Stock"

    USER_PROMPT = (
        "First, analyze the stock {stock} in the current situation. "
        "Then, provide a decision for these 3 options with a percentage:\n"
        "1. Buy\n2. Sell\n3. Hold\n"
        "For example, if you are very sure "
        'about buying a stock, you can give "Buy: 80%, Sell: 10%, Hold: 10%". '
        "Do not provide anything else with the 'Decision:'. "
        "Finally, provide a detailed reasoning and explanation for your given decision. "
        "Label this with 'Explanation:'. "
    ).format(stock=stock)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT},
        ],
    )

    full_text = response.choices[0].message.content.strip()

    # --- Split into Decision / Explanation --------------------------------
    decision_block = full_text
    explanation_block = ""
    if "Explanation:" in full_text:
        decision_block, explanation_block = full_text.split("Explanation:", 1)
        decision_block = decision_block.replace("Decision:", "").strip()
        explanation_block = explanation_block.strip()

    return jsonify(
        decision=decision_block,
        explanation=explanation_block,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
