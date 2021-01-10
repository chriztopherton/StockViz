import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
from datetime import date
import time
import math

plt.style.use('seaborn-whitegrid')
pd.options.mode.chained_assignment = None

st.sidebar.title("Daily Closing Stock Value Visualizer")
input = st.sidebar.text_input('Enter stock',"TSLA") #stock input string defined globally (need to find a better workaround)
st.sidebar.write('You entered: ', input)


try:

    @st.cache
    def scrape(dt):
        start = dt
        end = datetime.datetime.now()
        dt = web.DataReader([input], 'yahoo', start, end)
        dt.columns = dt.columns.get_level_values(0)
        
        return dt

    def viz(dt):

        fig = px.area(dt)

        fig.update_xaxes(
            title_text = 'Date',
            rangeslider_visible = True,
            rangeselector = dict(
                buttons = list([
                    dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
                    dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
                    dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
                    dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
                    dict(step = 'all')])))

        fig.update_yaxes(title_text = 'FB Close Price', tickprefix = '$')
        fig.update_layout(showlegend = False,
            title = {
                'text': f'{input} Share Price',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})

        st.plotly_chart(fig)

        
    def main():

        # Sidebar
        
        buy_date = st.sidebar.date_input('When was the stock purchased?', datetime.date(2020,1,10))

        raw_data = scrape(buy_date).copy()
        st.write(raw_data.iloc[::-1])

        today_stats = raw_data.tail(1)
        latest_closing_price = float(today_stats['Close'])
        buy_stats = raw_data.head(1)

        st.sidebar.write(today_stats.T)

        purchase_price = float(buy_stats['Close'])
        num_shares = st.sidebar.text_input("How many shares were purchased?","1")

        net_profit = round(latest_closing_price * int(num_shares) - purchase_price * int(num_shares),2)
        st.sidebar.write("You have profited", net_profit)

        # Main Panel

        viz(raw_data['Close'])

    if __name__ == "__main__":
        main()

except:
    pass