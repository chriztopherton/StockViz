import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import datetime

plt.style.use('seaborn-whitegrid')
pd.options.mode.chained_assignment = None


stock = st.text_input('Enter stock')
st.write('You entered: ', stock)


try:

    @st.cache
    def scrape_loader(stock): 

        link_to_data = f'https://ca.finance.yahoo.com/quote/{stock}/history?p={stock}'
        dt = pd.read_html(link_to_data)[0]
        dt.drop(dt.tail(1).index,inplace=True) # drop last row, not relevant
        dt.Date = pd.to_datetime(dt.Date) # convert first column to date object
        event = dt[pd.to_numeric(dt.Open, errors='coerce').isnull()].index.to_list()[0] #find event dates, such as splits
        dt = dt.head(event).copy() # slice data from event date

        return dt

    def MA_4(dat,col):
            d = dat[['Date',col]]
            d[col] = pd.to_numeric(d[col])
            
            for i in range(1,d.shape[0]-3):
                avg = (d[col].iloc[i] + d[col].iloc[i+1] + d[col].iloc[i+2] + d[col].iloc[i+3])/4
                d.loc[i+1,"SMA"] = np.round(avg,2)

            return d
    
    def viz(dat):

        dat_sma = MA_4(dat,"Open")

        fig = go.Figure(layout=dict(title=dict(text=f'{stock} Stock Since Split')))
        fig.add_trace(go.Scatter(x=dat.Date, y=dat.Open,
                            mode='lines',
                            name='Price'))
        fig.add_trace(go.Scatter(x=dat_sma.Date, y=dat_sma.SMA,
                            mode='lines',
                            name='SMA'))
        st.plotly_chart(fig)


    def main():
        st.header("Stock Visualizer")

        data = scrape_loader(stock)

        if st.button('Show data'):
            st.write(data)

        if st.button('Show viz'):
            viz(data)

    if __name__ == "__main__":
        main()

except:
    pass