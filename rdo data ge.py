import pandas as pd
import numpy as np
import datetime

# --- Configuration for the dataset ---
NUM_RECORDS = 9000
NUM_CUSTOMERS = 500  # Number of unique customers
START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date.today()

# --- Generate dummy data ---

# 1. Generate customer IDs
customer_ids = np.random.choice(range(1000, 1000 + NUM_CUSTOMERS), size=NUM_RECORDS)

# 2. Generate dates
# The dates are generated randomly within the specified range.
date_range = (END_DATE - START_DATE).days
dates = [START_DATE + datetime.timedelta(days=int(np.random.rand() * date_range)) for _ in range(NUM_RECORDS)]

# 3. Generate unique transaction IDs
# Ensure each transaction has a unique ID
transaction_ids = [f'TID{i+1}' for i in range(NUM_RECORDS)]

# 4. Generate random amounts
# Monetary values are generated with a realistic distribution,
# with some customers spending more than others.
amounts = np.random.lognormal(mean=4.5, sigma=0.8, size=NUM_RECORDS)
amounts = np.round(amounts, 2)

# --- Create the DataFrame and save to CSV ---
data = {
    'customer_id': customer_ids,
    'date': dates,
    'transaction_id': transaction_ids,
    'amount': amounts
}

df = pd.DataFrame(data)

# Sort by date to make the data more realistic
df = df.sort_values(by='date').reset_index(drop=True)

# Save the DataFrame to a CSV file
file_name = 'large_rfm_data.csv'
df.to_csv(file_name, index=False)

print(f"Successfully created a CSV file named '{file_name}' with {NUM_RECORDS} records.")
print("You can now upload this file to your RFM agent to test its functionality.")

