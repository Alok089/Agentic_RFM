from flask import Flask, jsonify, request,render_template
import random
import time
import pandas as pd

app = Flask(__name__)

# --- In-memory database for demonstration ---
customers = [
    {"id": 1, "name": "Alex Johnson", "recency": 5, "frequency": 5, "monetary": 5, "segment": "champion"},
    {"id": 2, "name": "Sarah Lee", "recency": 2, "frequency": 4, "monetary": 3, "segment": "at-risk"},
    {"id": 3, "name": "David Chen", "recency": 5, "frequency": 1, "monetary": 4, "segment": "new"},
    {"id": 4, "name": "Emily White", "recency": 1, "frequency": 1, "monetary": 1, "segment": "dormant"},
]

activity_log = []
agent_log = []

# --- The core RFM logic: The Agent's "model" ---
# This function takes a customer's R, F, and M scores and returns their segment.
def get_segment(r, f, m):
    # Champion: High scores in all categories (recent, frequent, high spender)
    if r >= 4 and f >= 4 and m >= 4:
        return 'champion'
    # Loyal: High frequency and monetary, but maybe not super recent
    if r >= 3 and f >= 4 and m >= 4:
        return 'loyal'
    # Promising: Recent, but low frequency/monetary - potential for growth
    if r >= 4 and f < 3 and m < 3:
        return 'promising'
    # At-Risk: Hasn't purchased recently, but used to be a good customer
    if r < 3 and f >= 3:
        return 'at-risk'
    # Dormant: Haven't purchased in a long time
    if r < 2 and f < 3:
        return 'dormant'
    # New: Recently made a first purchase
    if f == 1:
        return 'new'
    return 'dormant' # Default case

# Function to simulate a marketing action based on the segment.
def get_agent_action(customer_name, segment):
    if segment == 'champion':
        return f"Sending a 'Thank You for being a Champion!' email with an exclusive offer to {customer_name}."
    elif segment == 'loyal':
        return f"Sending a 'Loyalty Reward' discount offer to {customer_name}."
    elif segment == 'promising':
        return f"Sending a personalized 'Welcome Back' message with product recommendations to {customer_name}."
    elif segment == 'at-risk':
        return f"Sending a 'We Miss You' email to {customer_name} to prevent churn."
    elif segment == 'new':
        return f"Initiating a 3-step welcome email series for {customer_name}."
    elif segment == 'dormant':
        return f"Adding {customer_name} to a dormant customer reactivation campaign."
    else:
        return f"Monitoring {customer_name}. No action needed at this time."


# Main routes
@app.route('/', methods=['GET', 'POST'])
def RFM():
    """Handle orderbook operations"""
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not file.filename.endswith(('csv','parquet')):
            return jsonify({'error': 'Invalid file type. Only csv / parquet files are allowed.'}), 400

        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_parquet(file)

        required_columns = [
        'customer_id','date','transaction_id','amount'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            })

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)