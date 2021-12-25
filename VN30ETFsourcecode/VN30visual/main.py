import numpy as np
import pandas as pd
import requests
import streamlit as st
import math
from PIL import Image
import base64
import matplotlib.pyplot as plt

stocks = pd.read_csv("VN30ETFsourcecode/VN30visual/VN30.csv")
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
#sidebar
st.sidebar.write("""
# VN30 ETF from Vietnam stock market

""")
portfolio_size = st.sidebar.number_input('Insert your portfolio size (VND)')
st.sidebar.write('Your size is ', portfolio_size)

#main screen
image = Image.open('VN30ETFsourcecode/VN30visual/stonks.png')

st.image(image, use_column_width=True)


st.subheader('VN30 ETF')

for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Weight'] =  round(final_dataframe.loc[i, 'Market Capitalization']/sum(final_dataframe['Market Capitalization']),4)
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(math.floor(portfolio_size*final_dataframe.loc[i, 'Weight'] / final_dataframe.loc[i, 'Stock Price']) / 100) * 100
    final_dataframe.loc[i,'TOTAL MONEY (VND)'] = final_dataframe.loc[i,'Number of Shares to Buy'] * final_dataframe.loc[i,'Stock Price']


st.dataframe(final_dataframe, height = 500)
Money_use = sum(final_dataframe['TOTAL MONEY (VND)'])
Money_left = portfolio_size - Money_use
st.sidebar.write('Money use: '+ str(Money_use))
st.sidebar.write('Money left: '+ str(Money_left))
st.sidebar.write(("""
***
"""))
st.sidebar.write(('This is a demo using financial API from IEXCloud.'))
st.sidebar.write(('Data is not real-time and not precise.'))
st.sidebar.write(('Money left is quite big, due to the minimum amount for each stock are 100.'))
st.sidebar.write(('Therefore, based on your NAV, the money left is different. You can use it to play high risk stock to earn excess return. '))
st.sidebar.write(("""
***"""))
st.sidebar.write(('My name is Quoc Hung.\nContact:'))
st.sidebar.markdown("""
* **Gmail:** hungha1412@gmail.com or, qhung9621@gmail.com
* **Linkedin Profile:** [Ha Quoc Hung](https://www.linkedin.com/in/quốc-hùng-hà-6b192b222/detail/recent-activity/)
""")




#download csv file
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VN30ETF.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(final_dataframe), unsafe_allow_html=True)



if st.button('Show chart'):
    st.header('Weight')
    labels = list(final_dataframe.Ticker)
    sizes = list(final_dataframe.Weight)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, startangle = 90)
    ax1.axis('equal')
    st.pyplot(fig1)





