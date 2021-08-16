import pandas as pd

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

# what are the diffs between those seemingly similar columns?
value_diffs = (processed_df[processed_df['UnknownDecimalValue2MatchesUnknownDollarValue'] !=
                      processed_df['UnknownDollarValue']])

# not sure what this column is -- mostly '-' but some have a date
mystery_date = processed_df[processed_df['MysteryDate'] != '-']

# are both the currency columns the same? Yes.
currency_diffs = processed_df[processed_df['Currency1'] != processed_df['Currency2']]
fx_rate_not_1 = processed_df[processed_df['FX Rate'].astype(float) != 1]

