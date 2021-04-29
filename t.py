# with engine.connect() as connection:
#     table_statement = f"""
#         CREATE TABLE IF NOT EXISTS t (
#             id INTEGER PRIMARY KEY  AUTOINCREMENT,
#             tweet TEXT,
#             province TEXT,
#             CHECK(province IN ('ON', 'MB', 'BC', 'QC', 'SK', NULL))
#         );
#     """
#     res = connection.execute(table_statement)
#     print(res)

import pandas as pd
import pickle

df = pd.read_csv('~/dev-src/twitter-test/CanadianPostalCodes.csv')
print(df)

FSA = set(df['FSA'].values.tolist())
print('M5V' in FSA)

with open('FSA.pickle', 'wb') as handle:
    pickle.dump(FSA, handle, protocol=pickle.HIGHEST_PROTOCOL)
