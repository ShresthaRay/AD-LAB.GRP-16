from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go


def generate_stock_graph(request):
    # Download stock data using yfinance
    data = yf.download('AAPL', start='2024-07-18', end='2024-12-18')
    data = data.dropna()


    # Prepare the data for Plotly
    open_values = data['Open'].values.tolist()
    high_values = data['High'].values.tolist()
    low_values = data['Low'].values.tolist()
    close_values = data['Close'].values.tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()


    # Plotly Candlestick chart data
    fig_data = [{
        'type': 'candlestick',
        'x': dates,
        'open': open_values,
        'high': high_values,
        'low': low_values,
        'close': close_values,
        'increasing': {'line': {'color': 'green'}},
        'decreasing': {'line': {'color': 'red'}}
    }]

    layout = {
        'title': 'AAPL Stock Price Candlestick Chart',
        'xaxis': {'title': 'Date'},
        'yaxis': {'title': 'Price'},
        'xaxis_rangeslider_visible': False
    }

    return JsonResponse({'data': fig_data, 'layout': layout})








def home(request):
    try:
        stockSNX = yf.Ticker('^BSESN')
        dataSNX = stockSNX.history(period="5d")
        stockNFT = yf.Ticker('^NSEI')
        dataNFT  = stockNFT.history(period="5d")

        if len(dataSNX) < 2 or len(dataNFT) < 2:
            if len(dataSNX) == 0 or len(dataNFT) == 0:
                return JsonResponse({'error': 'Market is currently closed, and no data is available.'}, status=400)
            return JsonResponse({'error': 'Not enough data for the last 2 days'}, status=400)
        
        latest_dataSNX = dataSNX.iloc[-1]
        previous_dataSNX = dataSNX.iloc[-2]

        latest_dataNFT = dataNFT.iloc[-1]
        previous_dataNFT = dataNFT.iloc[-2]

        sensex_ = latest_dataSNX['Open']
        nifty_ = latest_dataNFT['Close']
        sensex_diff = latest_dataSNX['Open']-previous_dataSNX['Close']
        nifty_diff = latest_dataNFT['Open']-previous_dataNFT['Close']
        sensex_data = {
            'sensex': sensex_,
            'nifty' : nifty_,
            'sensex_diff':sensex_diff,
            'nifty_diff':nifty_diff,
            'stockSymbol':'AAPL'
        }
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Render the data to the template
    return render(request, 'homeui.html', sensex_data)