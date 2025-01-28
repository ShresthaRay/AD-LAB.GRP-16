import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Bidirectional, Attention, Dropout, Input
import tensorflow as tf

# Disable GPU usage (if necessary)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Read the historical data from the CSV file
data = pd.read_csv('historical_data.csv')

# Check for missing values in the original dataset
print("Missing values in original dataset:")
print(data.isnull().sum())

# Check unique tickers in the dataset
print("Unique tickers in the dataset:", data['Ticker'].unique())

# List of stock tickers for ten companies
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'NFLX', 'NVDA', 'BRK-B', 'JPM']

# Function to preprocess data for each company
def preprocess_data(company_data):
    num_col = ['Close', 'Open', 'High', 'Low', 'Volume']
    
    # Convert columns to numeric and coerce errors
    company_data[num_col] = company_data[num_col].apply(pd.to_numeric, errors='coerce')
    
    # Check for NaNs before filling
    if company_data[num_col].isnull().any().any():
        print(f"NaNs found before filling in {company_data['Ticker'].iloc[0]}.")
        print(company_data[num_col].isnull().sum())  # Log NaN counts per column

    # Fill NaNs with mean of each column
    company_data[num_col] = company_data[num_col].fillna(company_data[num_col].mean())
    
    # Check for NaNs after filling
    if company_data[num_col].isnull().any().any():
        print(f"NaNs still present after filling in {company_data['Ticker'].iloc[0]}.")
    
    # Create target variable
    company_data['Target'] = (company_data['Close'].shift(-1) > company_data['Close']).astype(int)
    
    return company_data[:-1]

# Dictionary to hold processed data for each company
processed_data_dict = {}
for ticker in tickers:
    company_data = data[data['Ticker'] == ticker]
    if company_data.empty:
        print(f"No data found for {ticker}. Skipping...")
        continue
    processed_data_dict[ticker] = preprocess_data(company_data)

# Function to create datasets
def create_datasets(processed_data, time_step=60):
    X, y = [], []
    scalers = {}
    
    for ticker, company_data in processed_data.items():
        if company_data.empty:
            print(f"Skipping scaling for {ticker} due to empty data.")
            continue
        
        scaler = MinMaxScaler()
        
        # Check for NaNs before scaling
        if company_data[['Close', 'Open', 'High', 'Low', 'Volume']].isnull().any().any():
            print(f"NaNs found in raw features for {ticker}.")
            print(company_data.isnull().sum())  # Log NaN counts per column
            continue
        
        scaled_features = scaler.fit_transform(company_data[['Close', 'Open', 'High', 'Low', 'Volume']])
        
        # Check for NaNs in scaled features
        if np.isnan(scaled_features).any():
            print(f"NaNs found in scaled features for {ticker}.")
            continue
        
        scalers[ticker] = scaler
        
        for i in range(len(scaled_features) - time_step - 1):
            X.append(scaled_features[i:(i + time_step)])
            y.append(scaled_features[i + time_step, 0])  # Predicting the next Close price
            
    return np.array(X), np.array(y), scalers

# Create datasets for training and testing
X, y, scalers = create_datasets(processed_data_dict)

# Check for NaNs in X and y after creating datasets
if np.isnan(X).any():
    print("NaNs found in X dataset.")
if np.isnan(y).any():
    print("NaNs found in y dataset.")

# Proceed if no NaNs are found
if len(X) == 0 or len(y) == 0:
    print("No valid training data was created. Exiting.")
else:
    # Split into training and testing sets (80% train, 20% test)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Check for NaNs in training data
    if np.isnan(X_train).any() or np.isnan(y_train).any():
        print("NaNs found in training data.")
        exit()

    print("Data is ready for training.")
