import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import pandasql as psql

plt.style.use('seaborn-whitegrid')
pd.options.mode.chained_assignment = None

list_of_sp = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

st.sidebar.title("Daily Closing Stock Value Visualizer")
stock = st.sidebar.selectbox('Select a stock:', list_of_sp.Symbol.unique())
st.sidebar.write('You entered: ', stock)


try:
    @st.cache(allow_output_mutation=True)
    def scrape_loader(stock,record_event): 
        link_to_data = f'https://ca.finance.yahoo.com/quote/{stock}/history?p={stock}'
        dt = pd.read_html(link_to_data)[0]
        dt.drop(dt.tail(1).index,inplace=True) # drop last row, not relevant
        dt.Date = pd.to_datetime(dt.Date) # convert first column to date object

        if record_event:
            bool_event = pd.to_numeric(dt['Close*'], errors='coerce').isnull()
            event_slice = dt[bool_event]
            if bool_event.sum() >= 1:
                event_indx = event_slice.index.to_list()[0] #find event dates, such as splits
                dt = dt.head(event_indx).copy()
        else:
            cols = dt.columns.drop('Date')
            dt[cols] = dt[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        dt['prev_val'] = dt['Close*'].shift(-1)
        dt['volume_col'] = np.where(dt.prev_val < dt['Close*'],1,0)
        dt.Volume = dt.Volume.astype('int')/100000

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
    
    def value_viz(dat):
        dat = dat[np.count_nonzero(dat.values, axis=1) > len(dat.columns)-2]

        fig = go.Figure(layout=dict(title=dict(text=f'{stock} Stock')))
        fig.add_trace(go.Scatter(x=dat.Date, y=dat['Close*'],mode='lines',name='Price'))
        fig.add_trace(go.Bar(x=dat.Date,y=dat.Volume))
        fig.update_layout(hovermode='x unified')

        st.plotly_chart(fig)


    def main():

        """
        Sidebar
        """
        record_event = False
        if st.sidebar.checkbox("Record event"):
            record_event = True
        
        data = scrape_loader(stock,record_event).copy()
        cols = st.sidebar.multiselect("Choose metrics to view:",data.columns.drop(['prev_val','volume_col']))
        
        sel_stock = list_of_sp[list_of_sp.Symbol == stock]
        st.sidebar.write(sel_stock)

        """
        Main Panel
        """
        st.write(data[cols])  
        value_viz(data)
                        
        

    if __name__ == "__main__":
        main()

except:
    pass