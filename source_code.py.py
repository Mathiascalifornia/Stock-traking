# Main function
def main(tickers):    

    ############### Imports ###############
    import pandas as pd , numpy as np , random
    import plotly.express as px , plotly.graph_objects as go
    import matplotlib.pyplot as plt , seaborn as sns
    import dash 
    from dash import dcc 
    from dash import html 
    from dash.dependencies import Input, Output
    import datetime as dt 
    import talib as ta
    from sklearn.preprocessing import MinMaxScaler
    import pandas_datareader as web
    import fear_and_greed
    import os
    from threading import Timer
    import webbrowser
    import warnings
    warnings.filterwarnings('ignore')



    def get_data(tickers=tickers):
        ''' Get the data from yahoo finance , using the list of tickers'''
        data_list =  [web.DataReader(tick , 'yahoo' , dt.datetime(1975,1,1))[['Adj Close' , 'Volume']] for tick in tickers]
        return data_list

    sp500 = web.DataReader('^GSPC' , 'yahoo' , dt.datetime(1975,1,1))[['Adj Close' , 'Volume']]

    # Create a list of all my stocks
    liste_stocks = get_data()
    liste_stocks.append(sp500)
    tickers.append('SP500')

    def minmax_scale(days , listestock=liste_stocks):
        ''' Scale the data , to make comparaison possible between stocks '''
        period_df = []
        for df in listestock:
            df_ = df[df.index[-1] - dt.timedelta(days):]
            df_['normalized'] = MinMaxScaler().fit_transform(df_['Adj Close'].values.reshape(-1,1))
            period_df.append(df_)
        return period_df

    liste_stock_overall = minmax_scale(365*47)
    liste_two_week = minmax_scale(14)
    liste_six_month = minmax_scale(30*6)
    liste_one_year = minmax_scale(365)
    liste_five_year = minmax_scale(365*5)


    # To link the ticker and the dataframes
    ticker_df_dict = dict(zip(tickers , liste_stocks))


    # Function to add the traces
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=liste_stock_overall[-1]['normalized'] , hovertext=liste_stock_overall[-1]['Adj Close'].apply(lambda x : str(f'Price : {np.round(x,2)}')), x=liste_stock_overall[-1].index , name=tickers[-1]  , mode='lines' , visible=True))
    for i in range(len(liste_stocks) -1):
            fig.add_trace(go.Scatter(y=liste_stock_overall[i]['normalized'] , hovertext=liste_stock_overall[i]['Adj Close'].apply(lambda x : str(f'Price : {np.round(x,2)}')), x=liste_stock_overall[i].index , name=tickers[i] , mode='lines', visible='legendonly'))

    def add_a_trace(liste , fig=fig):
        ''' Add a trace in the figure'''
        for i in range(len(liste)):
            fig.add_trace(go.Scatter(y=liste[i]['normalized'] , hovertext=liste[i]['Adj Close'].apply(lambda x : str(f'Price : {np.round(x,2)}')), x=liste[i].index , name=tickers[i] , mode='lines', visible=False))

    # Add the traces
    add_a_trace(liste_two_week)
    add_a_trace(liste_six_month)
    add_a_trace(liste_one_year)
    add_a_trace(liste_five_year)


    liste1 = [*['legendonly' for i in range(len(tickers) - 1)] , True  , *[False for i in range(len(tickers)*4)]]
    liste2 = [*[False for i in range(len(tickers))] , *['legendonly' for i in range(len(tickers) - 1)] , True , *[False for i in range(len(tickers)*3)]]
    liste3 = [*[False for i in range(len(tickers)*2)] , *['legendonly' for i in range(len(tickers) - 1)] , True ,  *[False for i in range(len(tickers)*2)]]
    liste4 = [*[False for i in range(len(tickers)*3)] , *['legendonly' for i in range(len(tickers) - 1)] , True , *[False for i in range(len(tickers))]]
    liste5 = [*[False for i in range(len(tickers)*4)] , *['legendonly' for i in range(len(tickers) - 1)] , True]

    # Create the buttons
    dropdown_buttons = [
    {'label': "ALL", 'method': "update", 'args': [{"visible": liste1} , {'title' : 'Overall normalized stock prices'}] },
    {'label': "2WTD", 'method': "update", 'args': [{"visible": liste2} , {'title' : 'Two weeks normalized stock prices'}]},
    {'label': "6MTD", 'method': "update", 'args': [{"visible": liste3} , {'title' : 'Six months normalized stock prices'}]},
    {'label': "1YTD", 'method': "update", 'args': [{"visible": liste4} , {'title' : 'One year normalized stock prices'}]},
    {'label': "5YTD", 'method': "update", 'args': [{"visible":liste5} , {'title' : 'Five years normalized stock prices'}]}
    ]

    # Update the figure to add dropdown menu
    fig.update_layout({
            'updatemenus': [
                {'type': "dropdown",
                'showactive': True,'active': 0, 'buttons' : dropdown_buttons},
            ]})

    # To see all the prices 
    fig.update_layout(hovermode = 'x unified')

    # The figsize
    fig.update_layout(autosize=False , width=1500 , height=500)

    # The title
    fig.update_layout(
        title={
            'text': "Share price over time",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})


    ############### Some functions ###############
    def get_pct_change(df):
        ''' Get the change in percentage for differents time periods'''
            # Week
        try:
            current = float(df.iloc[-1]['Adj Close'])
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(7))]['Adj Close'])
            week_diff = np.round(100*((current - previous) / previous),2)
        except:
            current = float(df.iloc[-1]['Adj Close'])
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(9))]['Adj Close'])
            week_diff = np.round(100*((current - previous) / previous),2)
        try:
            # Two weeks
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(14))]['Adj Close'])
            twoweek_diff = np.round(100*((current - previous) / previous),2)
        except:
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(16))]['Adj Close'])
            twoweek_diff = np.round(100*((current - previous) / previous),2)         

        try:
            # Six month
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(6*30))]['Adj Close'])
            sixmonth_diff = np.round(100*((current - previous) / previous),2)
        except:
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(6*30+2))]['Adj Close'])
            sixmonth_diff = np.round(100*((current - previous) / previous),2)          

            # One year
        try:
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(365))]['Adj Close'])
            oneyear_diff = np.round(100*((current - previous) / previous), 2)
        except:
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(367))]['Adj Close'])
            oneyear_diff = np.round(100*((current - previous) / previous), 2)         

        try:
            # Five years

            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(5*365))]['Adj Close'])
            fiveyear_diff = np.round(100*((current - previous) / previous), 2)

        except:
            previous = float(df[df.index == str(df.index[-1] - dt.timedelta(5*365+2))]['Adj Close'])
            fiveyear_diff = np.round(100*((current - previous) / previous), 2)

            # Overall
            previous = float(df.iloc[0]['Adj Close'])
            overall_diff = np.round(100*((current - previous) / previous), 2)
            
            # Return the dictionnary with all the diff
            return {'One week : ' : week_diff , 'Two weeks : ' : twoweek_diff , 'Six months : ' : sixmonth_diff , 'One year : ' : oneyear_diff , 'Five years : ' : fiveyear_diff , 'Overall : ' : overall_diff}

    # Plot the RSI
    def plot_rsi(df):
        ''' Plot the Relative Strenght Index figure '''
        df['RSI'] = ta.RSI(df['Adj Close'])

        # We'll do that with simple buttons
        df['RSI'] = ta.RSI(df['Adj Close'])


        figure = px.line(df[df.index[-1] - dt.timedelta(252*5) :]['RSI'])
        figure.add_hline(y=70 , line_color='red')
        figure.add_hline(y=30  ,line_color='green')

        buttons = [
        {'count': 15, 'label': "3WTD", 'step': 'day', 'stepmode': 'todate'},
        {'count': 21*6, 'label': "6MTD", 'step': 'day', 'stepmode': 'todate'},
        {'count': 252*5, 'label': "5YTD", 'step': 'day', 'stepmode': 'todate'}
        ]

        figure.update_layout({'xaxis' : {'rangeselector' : {'buttons' : buttons}}})
        return figure


    # Plot the volume
    def plot_volume(df):
        ''' Plot the volume figure '''
        vol_fig = px.bar(df , x=df.index , y=df['Volume'] , color_discrete_sequence=['white'])
        buttons = [
            {'count': 15, 'label': "3WTD", 'step': 'day', 'stepmode': 'todate'},
            {'count': 21*6, 'label': "6MTD", 'step': 'day', 'stepmode': 'todate'},
            {'count': 252*5, 'label': "5YTD", 'step': 'day', 'stepmode': 'todate'},
            {'count': 252*47, 'label': "ALL", 'step': 'day', 'stepmode': 'todate'}]

        vol_fig.update_layout(width=1500 , height=500 , paper_bgcolor="white", plot_bgcolor="black")
        vol_fig.update_layout({'xaxis' : {'rangeselector' : {'buttons' : buttons}}})

        return vol_fig


    def bbands(df): 
        ''' Plot the bollinger bands figure '''   
        df_ = df[(df.index[-1] - dt.timedelta(365*5)):]

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df_['Adj Close'] , x=df_.index , mode='lines' , fillcolor='blue' , name='Price'))

        # Define the Bollinger Bands with 2-sd
        upper_2sd, mid_2sd, lower_2sd = ta.BBANDS(df_['Adj Close'],
                                                    nbdevup=2,
                                                    nbdevdn=2,
                                                    timeperiod=20)

        upper_2sd = pd.DataFrame(upper_2sd)
        mid_2sd = pd.DataFrame(mid_2sd)
        lower_2sd = pd.DataFrame(lower_2sd)

        fig.add_trace(go.Scatter(x=upper_2sd.index , y=upper_2sd[0] , line=dict(color='rgb(255,0,0)') , name='Upper band') )
        fig.add_trace(go.Scatter(x=mid_2sd.index , y=mid_2sd[0] , line=dict(color='rgb(0,255,0)') , name='SMA 20'))
        fig.add_trace(go.Scatter(x=lower_2sd.index , y=lower_2sd[0] , line=dict(color='rgb(255,0,0)') , name='Lower band'))

        buttons = [
        {'count': 31, 'label': "1MTD", 'step': 'day', 'stepmode': 'todate'},
        {'count' : 365 , 'label' : '1YTD' , 'step' : 'day' , 'stepmode' : 'todate'},
        {'count' : 365*5 , 'label' : '5YTD' , 'step' : 'day' , 'stepmode' : 'todate'}
            ]

        fig.update_layout({'xaxis' : {'rangeselector' : {'buttons' : buttons}}})
        fig.update_layout(hovermode = 'x unified')
        fig.update_layout(width=1500 , height=500)

        return fig


    # Get the percentage différence to display

    pct_change_list = [get_pct_change(df) for df in liste_stocks]

    def display_pct_changes(ticker_diff_dict : dict):
        ''' Display the change in percentage already created '''
        string = f'   '
        for key , val in ticker_diff_dict.items():
            string += key
            if val >= 0:
                string += '+'
            string += str(val)
            string += ' %'
            string += ' | '

        fg = fear_and_greed.get()
        fg_string = f' .The Fear and Greed index is currently at {int(fg[0])} out of a hundred, so "{fg[1]}".'
        string += fg_string
        return string


    # A dictionary with the ticker and the other dict with the pct_change (link the informations)
    ticker_pct_change = {}
    for i in range(len(tickers)):
        ticker_pct_change[tickers[i]] = pct_change_list[i]

    ############### The dash app ##############

    # Instantiate the app
    app = dash.Dash(__name__)

    # First div
    app.layout = html.Div(id='Price' , children=[

    # Main title
    html.H1(children=['Stocks tracking'] , style={'border' : '1px solid black'}),

    # Main graph
    dcc.Graph(figure=fig),


    # Add the dropdown for the rsi and plain text (dropdown to the left , plain text to the right , rsi below)
    dcc.Dropdown(id='first_dropdown',
    options= [{'label' : tick , 'value' : tick} for tick in tickers] , value=tickers[-1]),



    html.Br(), # Jump a line

    # Title for the percentages change
    html.H3(children = ['Changes in percentage for SP500 :'] , id='title_percentage') ,

    html.Br(), # Jump a line 

    # Plain text
    html.I(children=[display_pct_changes(pct_change_list[-1])] , style={'border':'1px solid black'} , id='pct_changes'),

    html.Br(),
    html.Br(),

    # Title for the RSI fig
    html.H3(children=[f'Relative Strenght Index (RSI) , trading volume and Bollinger bands of SP500 :'] , id='title'),

    # Figures
    dcc.Graph(id='RSI' , figure=plot_rsi(sp500)),
    dcc.Graph(id='volume' , figure=plot_volume(sp500)),
    dcc.Graph(id='bbands' , figure=bbands(sp500))


    ] , style={'text-align' : 'center'})

    # For the pct changes
    @app.callback(
    Output(component_id='pct_changes' , component_property='children'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_pct_changes(input_ticker):
        if input_ticker:
            return display_pct_changes(ticker_pct_change.get(input_ticker))


    # For the RSI figure
    @app.callback(
    Output(component_id='RSI' , component_property='figure'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_rsi_fig(input_ticker):
        if input_ticker:
            return plot_rsi(ticker_df_dict.get(input_ticker))


    # For the volume plot
    @app.callback(
    Output(component_id='volume' , component_property='figure'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_volume_plot(input_ticker):
        if input_ticker:
            return plot_volume(ticker_df_dict.get(input_ticker))


    # For the bbands figure
    @app.callback(
    Output(component_id='bbands' , component_property='figure'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_bbands(input_ticker):
        if input_ticker:
            return bbands(ticker_df_dict.get(input_ticker))


    # For the RSI title
    @app.callback(
    Output(component_id='title' , component_property='children'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_title(input_ticker):
        if input_ticker:
            return f'Relative Strenght Index (RSI) , trading volume and Bollinger bands of {input_ticker} :'


    # For the percentage change title
    @app.callback(
    Output(component_id='title_percentage' , component_property='children'),
    Input(component_id='first_dropdown' , component_property='value'))
    def change_pct_title(input_ticker):
        if input_ticker:
            return f'Changes in percentage for {input_ticker} :'


    def open_browser():
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open_new('http://127.0.0.1:8050/')

    if __name__ == "__main__":
        Timer(1, open_browser).start()
        app.run_server()

############### GUI ###############
   
from tkinter import *
from tkinter import Tk

root = Tk()
root.title('Stock tracking')
label = Label(root , text='Entrez vos tickers , séparés d\'un espace / Enter your tickers , separated by a space')
label.pack()
ticker = Entry(root , width=70 , borderwidth=10)
ticker.pack()

def get_tickers(ticker=ticker):
    tickers_list = ticker.get()
    main(list(str(tickers_list).upper().split(' ')))

button = Button(root , text='START' , width=70 , command=get_tickers)
button.pack()

root.mainloop()

