from flask import Flask, render_template, request, jsonify
import pandas as pd
import datetime
import os

app = Flask(__name__)


# --- The core RFM logic: The Agent's "model" ---
# This function takes a customer's R, F, and M scores and returns their segment.
def get_segment(r_score, f_score, m_score):
    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return 'champion'
    if r_score >= 3 and f_score >= 4 and m_score >= 4:
        return 'loyal'
    if r_score >= 4 and f_score < 3 and m_score < 3:
        return 'promising'
    if r_score < 3 and f_score >= 3:
        return 'at-risk'
    if r_score < 2 and f_score < 3:
        return 'dormant'
    if f_score == 1:
        return 'new'
    if ((r_score*0.2) + (f_score*0.3) + (m_score*0.5)) >= 3:
        return 'High Potential'
    if ((r_score*0.2) + (f_score*0.3) + (m_score*0.5)) < 3 and ((r_score*0.2) + (f_score*0.3) + (m_score*0.5)) > 2:
        return 'Mid Potential'
    if ((r_score*0.2) + (f_score*0.3) + (m_score*0.5)) <= 2:
        return 'Low Potential'
    return 'NA'


# --- Main route to handle form submission and display results ---
@app.route('/', methods=['GET', 'POST'])
def rfm_calculator():
    customers_list = None
    message = None
    error = None
    RFM_summary = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'No selected file'
            elif not file.filename.endswith(('csv', 'parquet')):
                error = 'Invalid file type. Only csv or parquet files are allowed.'
            else:
                try:
                    if file.filename.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_parquet(file)

                    required_columns = ['customer_id', 'date', 'transaction_id', 'amount']
                    missing_columns = [col for col in required_columns if col not in df.columns]

                    if missing_columns:
                        error = f'Missing required columns: {", ".join(missing_columns)}'
                    else:
                        # --- RFM Calculation Logic ---
                        df['date'] = pd.to_datetime(df['date'])
                        snapshot_date = df['date'].max() + datetime.timedelta(days=1)
                        rfm = df.groupby('customer_id').agg({
                            'date': lambda x: (snapshot_date - x.max()).days,
                            'transaction_id': 'count',
                            'amount': 'sum'
                        })
                        rfm.columns = ['Recency', 'Frequency', 'Monetary']

                        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
                        rfm['F_Score'] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
                        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

                        rfm['Segment'] = rfm.apply(
                            lambda row: get_segment(row['R_Score'], row['F_Score'], row['M_Score']), axis=1)
                        rfm = rfm.reset_index()
                        customers_list = rfm.to_dict('records')[:5]
                        RFM_summary = rfm.groupby('Segment').agg(customers=('customer_id','nunique'),
                                                                 Last_Purchase=('Recency', 'mean'),
                                                                 Purchases=('Frequency', 'mean'),
                                                                 ATS=('Monetary','mean')).reset_index().round(2).to_dict('records')
                        message = 'RFM calculation successful!'
                        print(RFM_summary)

                except Exception as e:
                    error = f'Error processing file: {str(e)}'

    return render_template('index.html', customers=customers_list, message=message, error=error,RFM_summary=RFM_summary)


if __name__ == '__main__':
    app.run(debug=True)