import numpy as np
import pandas as pd
import requests
import streamlit as st
import math
from PIL import Image

stocks = pd.read_csv("./data/VN30.csv")
from Secret_api import IEX_CLOUD_API_TOKEN_PUBLISH

symbol ='ACB-VM'
api_url =f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN_PUBLISH}'
data = requests.get(api_url).json()

price = data['latestPrice']
market_cap = data['marketCap']
my_columns = ['Ticker', 'Stock Price', 'Market Capitalization','Weight', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)

final_dataframe.append(
    pd.Series(
    [
        symbol,
        price,
        market_cap,
        'N/A',
        'N/A'
    ],
        index = my_columns
    ),
    ignore_index=True
)
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    #print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns=my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN_PUBLISH}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(',', ):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']["latestPrice"],
                    data[symbol]['quote']["marketCap"],
                    'N/A',
                    'N/A'
                ], index=my_columns
            ), ignore_index=True
        )



#bring these lines to web
st.write("""
# VN30 ETF from Vietnam stock market

""")
image = Image.open('stonks.png')

st.image(image, use_column_width=True)

st.write("""
***
""")
portfolio_size = st.number_input('Insert your portfolio size (VND)')
st.write('Your size is ', portfolio_size)

st.write("""
***
""")

st.subheader('VN30 ETF')

for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Weight'] =  round(final_dataframe.loc[i, 'Market Capitalization']/sum(final_dataframe['Market Capitalization']),4)
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(math.floor(portfolio_size*final_dataframe.loc[i, 'Weight'] / final_dataframe.loc[i, 'Stock Price']) / 100) * 100
    final_dataframe['TOTAL MONEY (VND)'] = final_dataframe['Number of Shares to Buy'] * final_dataframe['Stock Price']




st.write(final_dataframe)
Money_use = sum(final_dataframe['TOTAL MONEY (VND)'])
Money_left = portfolio_size - Money_use
st.write('Money use: '+ str(Money_use))
st.write('Money left: '+ str(Money_left))






