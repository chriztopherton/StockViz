import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
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
    def scrape(rc):
        link_to_data = f'https://ca.finance.yahoo.com/quote/{input}/history?p={input}' #link to stock's yahoo page
        dt = pd.read_html(link_to_data)[0] # read contents of html table, grab first one
        
        dt.drop(dt.tail(1).index,inplace=True) # drop last row, not relevant
        dt['Date']= pd.to_datetime(dt['Date']) # convert first column to date object 

        if rc:
            bool_event = pd.to_numeric(dt['Close*'], errors='coerce').isnull() # not all rows are numerical, due to events such as splits
            event_slice = dt[bool_event] #index the event date
            if bool_event.sum() >= 1: # some stocks may have multiple events over time
                event_indx = event_slice.index.to_list()[0] #find event dates, such as splits
                dt = dt.head(event_indx).copy() # slice data from today's date back to latest event
        
        cols = dt.columns.drop('Date') # since data is quantitative, drop date in order to convert type
        dt[cols] = dt[cols].apply(pd.to_numeric, errors='coerce').fillna(0) 

        dt['prev_val'] = dt['Close*'].shift(-1) #create duplicate closing column, offset by 1 to compare dates
        dt['volume_col'] = np.where(dt.prev_val < dt['Close*'],1,0) # 1 if closing value for tomorrow > yersterday's
        

        return dt

    def MA_4(dat,col): #moving 4 day average ( 4 is arbitrary, it looks smoother)
            d = dat[['Date',col]]
            d[col] = pd.to_numeric(d[col])
            for i in range(1,d.shape[0]-3):
                avg = (d[col].iloc[i] + d[col].iloc[i+1] + d[col].iloc[i+2] + d[col].iloc[i+3])/4
                d.loc[i+1,"SMA"] = np.round(avg,2)


            """
            to plot:
            #dat_sma = MA_4(dat,"['Close*']")
            #fig.add_trace(go.Scatter(x=dat_sma.Date, y=dat_sma.SMA,mode='lines',name='SMA'))
            """

            return d
    
    def value_viz(dt):
        dt = dt[np.count_nonzero(dt.values, axis=1) > len(dt.columns)-2] # drop all zero rows

        fig = make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            row_heights=[0.8, 0.2],
                            vertical_spacing=0.1,
                            subplot_titles=("Closing Price", "Volume"))
        fig.append_trace(go.Scatter(x=dt.Date, y=dt['Close*'],mode='lines',name='Price'), row=1, col=1)

        vol_colors = {0:"red",1:"green"}
        for t in dt['volume_col'].unique(): # for loop: plot each bar and assign appropriate color
            dtp = dt[dt['volume_col']==t]
            fig.append_trace(go.Bar(x=dtp.Date, y = dtp.Volume,
                                marker_color=vol_colors[t]),row=2, col=1)
            
        fig.update_layout(hovermode='x unified',height=800, width=900,
                        title_text=f'Price & Volume of {input} Stock')

        st.plotly_chart(fig)


    def main():

        # Sidebar
        #st.sidebar.header("Select input options!")



        record_event = False
        if st.sidebar.checkbox("Record event"):
            record_event = True

        raw_data = scrape(record_event).copy()

        latest_closing_price = float(raw_data['Close*'][0])
        latest_volume_count = int(raw_data.Volume[0])


        st.sidebar.write("As of ",raw_data.Date[0].strftime('%A %d %B %Y'))

        st.sidebar.write("Last closing price:",latest_closing_price)
        st.sidebar.write("Latest volume count:",latest_volume_count)


        cols_options = raw_data.columns.drop(['prev_val','volume_col'])



        st.markdown("This displays metrics selected from the left-hand sidebar")
        if st.sidebar.checkbox("Show full data:"):
            st.write(raw_data)
        else:
            st.write(raw_data[['Date','Close*','Volume']])

        value_viz(raw_data)

        purchase_price = st.sidebar.text_input("What was the stock's purhcase price?")
        num_shares = st.sidebar.text_input("How many shares were purchased?")
        #date = st.sidebar.date_input('Purchase date', date.today())

        net_profit = round(latest_closing_price * int(num_shares) - int(purchase_price) * int(num_shares),2)
        st.sidebar.write("You have profited", net_profit)

        # Main

        st.markdown("Subplots for closing price and volume colored by corresponding trend")


    if __name__ == "__main__":
        main()

except:
    pass