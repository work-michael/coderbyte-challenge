import pandas as pd
import yfinance as yf

data_path = 'IMFSChallenge/constituents_history.pkl'
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

top_n_cutoff = 30
fake_dow_df = processed_df[processed_df['Date'] >= '2018-01-01']
fake_dow_df = fake_dow_df.groupby('Date').apply(lambda x: x.nlargest(top_n_cutoff, 'Weight'))


#use yfinance to get data for each unique ticker in our fake Dow df

tickers = fake_dow_df['Ticker'].unique()
tickers_str = ' '.join(tickers)
dow_start_date = fake_dow_df['Date'].min().strftime('%Y-%m-%d')

## uncomment to fetch fresh data
#yf_raw_df = yf.download(tickers_str, start=fake_dow_df['Date'].min(), end=fake_dow_df['Date'].max())
#yf_raw_df.to_pickle('IMFSChallenge/yfinance_raw_df.pkl')


yf_raw_df = pd.read_pickle('IMFSChallenge/yfinance_raw_df.pkl')






## what are the diffs between those seemingly similar columns?
#value_diffs = (processed_df[processed_df['Capitalization'] !=
#                      processed_df['Capitalization2']])


## not sure what this column is -- mostly '-' but some have a date
#mystery_date = processed_df[processed_df['MysteryDate'] != '-']

## are both the currency columns the same? Yes.
#currency_diffs = processed_df[processed_df['Currency1'] != processed_df['Currency2']]
#fx_rate_not_1 = processed_df[processed_df['FX Rate'].astype(float) != 1]

