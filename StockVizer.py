import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import datetime
import time
import math

plt.style.use('seaborn-whitegrid')
pd.options.mode.chained_assignment = None

st.sidebar.title("Daily Closing Stock Value Visualizer")
input = st.sidebar.text_input('Enter stock',"TSLA")
st.sidebar.write('You entered: ', input)


try:

    @st.cache
    def scrape(rc):
        link_to_data = f'https://ca.finance.yahoo.com/quote/{input}/history?p={input}'
        dt = pd.read_html(link_to_data)[0]
        
        dt.drop(dt.tail(1).index,inplace=True) # drop last row, not relevant
        dt['Date']= pd.to_datetime(dt['Date']) # convert first column to date object 

        if rc:
            bool_event = pd.to_numeric(dt['Close*'], errors='coerce').isnull()
            event_slice = dt[bool_event]
            if bool_event.sum() >= 1:
                event_indx = event_slice.index.to_list()[0] #find event dates, such as splits
                dt = dt.head(event_indx).copy()
        
        cols = dt.columns.drop('Date')
        dt[cols] = dt[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        dt['prev_val'] = dt['Close*'].shift(-1)
        dt['volume_col'] = np.where(dt.prev_val < dt['Close*'],1,0)
        

        return dt

    def MA_4(dat,col):
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
        dt = dt[np.count_nonzero(dt.values, axis=1) > len(dt.columns)-2]

        fig = make_subplots(rows=2, cols=1,shared_xaxes=True)
        fig.append_trace(go.Scatter(x=dt.Date, y=dt['Close*'],mode='lines',name='Price'), row=1, col=1)

        vol_colors = {0:"red",1:"green"}
        for t in dt['volume_col'].unique():
            dtp = dt[dt['volume_col']==t]
            fig.append_trace(go.Bar(x=dtp.Date, y = dtp.Volume,
                                marker_color=vol_colors[t]),row=2, col=1)
            
        fig.update_layout(hovermode='x unified',height=600, width=800,
                        title_text=f'Price & Volume of {input} Stock')

        st.plotly_chart(fig)


    def main():

        # Sidebar
        #st.sidebar.header("Select input options!")



        record_event = False
        if st.sidebar.checkbox("Record event"):
            record_event = True

        raw_data = scrape(record_event).copy()
        cols_options = raw_data.columns.drop(['prev_val','volume_col'])



        #cols_select = st.sidebar.multiselect("Choose metrics to view:",cols_options)

        # Main
        st.markdown("This displays metrics selected from the left-hand sidebar")
        if st.sidebar.checkbox("Show full data:"):
            st.write(raw_data)
        else:
            st.write(raw_data[['Date','Close*','Volume']])

        st.markdown("Subplots for closing price and volume colored by corresponding trend")

        value_viz(raw_data)

    if __name__ == "__main__":
        main()

except:
    pass