#import library
import numpy as np
import pandas as pd
import  requests
import xlsxwriter
import math

stocks = pd.read_csv('VN30.csv')
from Secret_api import IEX_CLOUD_API_TOKEN

symbol ='ACB-VM'

api_url =f'https://cloud.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

price = data['latestPrice']
market_cap = data['marketCap']



my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy EQUALWEIGHTED',]
final_dataframe = pd.DataFrame(columns = my_columns)

final_dataframe.append(
    pd.Series(
    [
        symbol,
        price,
        market_cap,
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
    # print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns=my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(',', ):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']["latestPrice"],
                    data[symbol]['quote']["marketCap"],
                    'N/A'
                ], index=my_columns
            ), ignore_index=True
        )

print('VN30 ETF')

portfolio_size = input('Enter the value of your portfolio: ' + 'VND')
try:
    val = float(portfolio_size)

except ValueError:
    print('Please try again\n Enter a new number')
    portfolio_size = input('Enter the value of your portfolio: ' + 'VND')
    val = float(portfolio_size)

position_size = float(portfolio_size) / len(final_dataframe.index)

print(sum(final_dataframe['Market Capitalization']))




for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of Shares to Buy EQUALWEIGHTED'] = math.floor(math.floor(position_size / final_dataframe.loc[i, 'Stock Price'])/100)*100
    final_dataframe['Total money for EQUALWEIGHTED'] = final_dataframe['Number of Shares to Buy EQUALWEIGHTED']* final_dataframe['Stock Price']
    final_dataframe.loc[i, 'Marketcap_weighted'] =  round(final_dataframe.loc[i, 'Market Capitalization']/sum(final_dataframe['Market Capitalization']),2)
    final_dataframe.loc[i, 'Number of Shares to Buy MARKETCAPWEIGHTED'] = math.floor(math.floor(position_size*final_dataframe.loc[i, 'Marketcap_weighted'] / final_dataframe.loc[i, 'Stock Price']) / 100) * 100
    final_dataframe['Sum'] = final_dataframe['Number of Shares to Buy MARKETCAPWEIGHTED'] * final_dataframe['Stock Price']
print(final_dataframe)


writer = pd.ExcelWriter('VN30 ETF.xlsx', engine = 'xlsxwriter')
final_dataframe.to_excel(writer, 'VN30 ETF', index = False)
background_color = '#FFEFDB'
font_color = '#000000'


string_format = writer.book.add_format(
    {
        'font_color': font_color,
        'bg_color': background_color,
        'border':1
    }
)


vnd_format = writer.book.add_format(
    {
        'num_format': '000.000.000 đ',
        'font_color': font_color,
        'bg_color': background_color,
        'border':1
    }
)


integer_format = writer.book.add_format(
    {
        'num_format': '0.00 đ',
        'font_color': font_color,
        'bg_color': background_color,
        'border':1
    }
)

percent_format = writer.book.add_format(
        {
            'num_format':'0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
column_formats = {
    'A': ['Ticker', string_format],
    'B': ['Stock Price', vnd_format],
    'C': ['Market Capitalization', vnd_format],
    'D': ['Marketcap_weighted', percent_format],
    'E': ['Number of Shares to Buy MARKETCAPWEIGHTED', integer_format],
    'F': ['Sum', integer_format]
}

for column in column_formats.keys():
    writer.sheets['VN30 ETF'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['VN30 ETF'].write(f'{column}1', column_formats[column][0], string_format)

writer.save()