from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import statsmodels.api as sm

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    ticker = request.form['ticker']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    data = yf.download(ticker, start=start_date, end=end_date)
    fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
    plot_div = fig.to_html(full_html=False)

    selected_tab = request.form['tabs']

    if selected_tab == "Price Movements":
        data2 = data
        data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
        data2.dropna(inplace=True)
        table = data2.to_html(index=False)

        return render_template('index.html', plot_div=plot_div, table=table)

    elif selected_tab == "Future Price Predictions":
        def fit_arima(data):
            model = sm.tsa.ARIMA(data['Adj Close'], order=(1, 1, 1))
            model_fit = model.fit()
            forecast_steps = 9  # You can adjust the number of future steps to predict
            forecast = model_fit.forecast(steps=forecast_steps)

            return forecast

        # Call the function to get future price predictions
        forecast = fit_arima(data)
        forecast = list(forecast)

        return render_template('index.html', plot_div=plot_div, forecast=forecast)

if __name__ == '__main__':
    app.run(debug=True)