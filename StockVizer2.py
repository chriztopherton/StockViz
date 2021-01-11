import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
#import pandas_datareader.data as web
import yfinance as yf
import datetime
from datetime import date
import time
import math
import re

plt.style.use('seaborn-whitegrid')
pd.options.mode.chained_assignment = None

st.sidebar.title("Daily Closing Stock Value Visualizer")
input = st.sidebar.text_area('Enter 1 or many stocks! (i.e. TSLA) ') #stock input string defined globally (need to find a better workaround)
st.sidebar.write('You entered: ', input)


try:

    @st.cache
    def scrape(first,last):
        dt = yf.download(input,start = first,end=last)
        return dt

    def subset_stock_mindx(dat,ch):
        return dat.loc[:,dat.columns.get_level_values(1).isin({ch})]


    def viz(dt,stock,sec):

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
                'text': f'{stock} Share Price',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})

        sec.plotly_chart(fig)

        
    def main():

        # Sidebar
        
        buy_date = st.sidebar.date_input('When was the stock purchased?', datetime.date(2020,1,10))
        end = datetime.datetime.now()
        raw_data = scrape(buy_date,end).copy()

        #Sort multiple stock results

        stock_str_list = re.sub("[^\w]", " ", input).split()
        num_stock_input = len(stock_str_list)

        stock_choice = st.sidebar.selectbox(f'Which of the {num_stock_input} stocks to analyze?',stock_str_list)

        col1, col2 = st.beta_columns(2)

        if num_stock_input == 1:
            analyze_data = raw_data
            col1.write(raw_data.iloc[::-1])
            viz(raw_data['Close'],input,col2)
        else:
            data_selected_choice = subset_stock_mindx(raw_data,stock_choice)
            data_selected_choice.columns = data_selected_choice.columns.get_level_values(0)
            analyze_data = data_selected_choice

            for i in stock_str_list:
                col1.header(f'Data for {i}')
                data_table = subset_stock_mindx(raw_data,i)
                data_table.columns = data_table.columns.get_level_values(0)
                col1.write(data_table.iloc[::-1])
                viz(data_table['Close'],i,col2)

        #st.sidebar.write(data_selected_choice)

        
        # display n stock historical data

        #cols_options = data_selected_choice.columns.get_level_values(0)
        #plot_col = st.sidebar.multiselect("Which column to visualize?", cols_options)
        

        today_stats = analyze_data.tail(1)
        latest_closing_price = float(today_stats['Close'])
        buy_stats = analyze_data.head(1)

        st.sidebar.write(today_stats.T)

        purchase_price = float(buy_stats['Close'])
        num_shares = st.sidebar.text_input("How many shares were purchased?","1")

        net_profit = round(latest_closing_price * int(num_shares) - purchase_price * int(num_shares),2)
        st.sidebar.write("You have profited", net_profit)

        # Main Panel


    if __name__ == "__main__":
        main()

except:
    pass