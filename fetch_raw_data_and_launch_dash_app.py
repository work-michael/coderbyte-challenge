import os
import pandas as pd
import yfinance as yf

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

data_base_path = r'C:\Users\u0os\Downloads\coderbyte-challenge-main\IMFSChallenge'

data_path = os.path.join(data_base_path, 'constituents_history.pkl')
raw_data_df = pd.read_pickle(data_path)

# Future dates in DF are empty, so filter them out now
raw_data_df = raw_data_df[raw_data_df.index <= '2021-07-30']

raw_data_df_dict = raw_data_df.to_dict()[0]

# eyeballing the data, I believe these are the columns
col_names = [
    'Ticker',
    'Name',
    'Sector',
    'SecType',
    'Capitalization',
    'Weight',
    'Capitalization2',
    'Shares',
    'CUSIP',
    'ISIN',
    'SEDOL',
    'ClosingPrice',
    'Country',
    'Exchange',
    'Currency1',
    'FX Rate',
    'Currency2',
    'MysteryDate'
]


def get_value_from_record(raw_value):
    if isinstance(raw_value, dict):
        return raw_value['raw']
    else:
        return raw_value


def process_constituent_raw_record(raw_constitutent_record, date):
    processed_dict = {col_names[i]: get_value_from_record(x) for i, x in enumerate(raw_constitutent_record)}
    processed_dict['Date'] = date
    return processed_dict


def process_one_day_raw_record(raw_day_record, date):
    return [process_constituent_raw_record(x, date) for x in raw_day_record]


records_as_dicts = [process_one_day_raw_record(raw_data_df_dict[x], x) for x in raw_data_df_dict]
records_as_dicts = [x for day_of_records in records_as_dicts for x in day_of_records]

processed_df = pd.DataFrame(records_as_dicts)

# Since this file contains 1000 names per date (possibly R1000?),
# loosely derive the Dow constituents by taking the top 30 names per date
# Also select names on or after Jan 1st 2018 per instructions
# Also fix the divisor to be 30 since there's no split adjustment divisor

top_n_cutoff = 30
fake_dow_df = processed_df[processed_df['Date'] >= '2018-01-01'].set_index('Ticker')
fake_dow_df = fake_dow_df.groupby('Date').apply(lambda x: x.nlargest(top_n_cutoff, 'Weight'))


#use yfinance to get data for each unique ticker in our fake Dow df

tickers = fake_dow_df.index.get_level_values(1).unique()
tickers_str = ' '.join(tickers)
dow_start_date = fake_dow_df.index.get_level_values(0).min().strftime('%Y-%m-%d')

## uncomment to fetch fresh data
#yf_raw_df = yf.download(tickers_str, start=fake_dow_df['Date'].min(), end=fake_dow_df['Date'].max())
#yf_raw_df.to_pickle(os.path.join(data_base_path, 'yfinance_raw_df.pkl'))

# if the above code was already run, then read in the saved .pkl file
yf_raw_df = pd.read_pickle(os.path.join(data_base_path, 'yfinance_raw_df.pkl'))

# calculate the Dow...
# A price-weighted index uses the price per share for each stock included
# and divides the sum by a common divisor, usually the total number of stocks in the index.
fake_dow_price_space = yf_raw_df['Close'].sum(axis=1)
fake_dow_idx = fake_dow_price_space / top_n_cutoff
fake_dow_security_weights = yf_raw_df['Close'].div(fake_dow_price_space, axis=0)

# identify the sector distribution of the index for 2018, 2019, and 2020
fake_dow_security_weights.columns.set_names(['Ticker'], inplace=True)
fake_dow_sector = fake_dow_security_weights.stack().to_frame('Weight')
fake_dow_sector = fake_dow_df[['Sector']].join(fake_dow_sector)
fake_dow_sector_distib = fake_dow_sector.groupby(['Date', 'Sector'])['Weight'].sum()


app = dash.Dash(__name__)

fig = px.line(fake_dow_sector_distib.reset_index(), x='Date', y='Weight', color='Sector')

app.layout = html.Div(children=[
    html.H1(children='IMFS Challenge'),

    html.Div(children='''
        Dow visualizations
    '''),

    dcc.Graph(
        id='dow-sectors',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server()

# Diagnostic checks I want to save:

## what are the diffs between those seemingly similar columns?
#value_diffs = (processed_df[processed_df['Capitalization'] !=
#                      processed_df['Capitalization2']])

## not sure what this column is -- mostly '-' but some have a date
#mystery_date = processed_df[processed_df['MysteryDate'] != '-']

## are both the currency columns the same? Yes.
#currency_diffs = processed_df[processed_df['Currency1'] != processed_df['Currency2']]
#fx_rate_not_1 = processed_df[processed_df['FX Rate'].astype(float) != 1]
