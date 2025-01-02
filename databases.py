import yfinance as yf
import pandas as pd

# List of ticker symbols for 10 companies
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "BRK-B", "JPM"]

# Define the time period
start_date = "2019-01-01"
end_date = "2023-12-31"

# Create an empty DataFrame to store all the data
all_data = pd.DataFrame()

# Loop through each ticker and fetch data
for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Ticker'] = ticker  # Add a column for the ticker
    all_data = pd.concat([all_data, data])

# Save to CSV
all_data.to_csv("historical_data.csv", index=True)

print("Data saved to historical_data.csv")