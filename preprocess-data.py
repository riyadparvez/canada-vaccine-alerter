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

df = pd.read_csv('CanadianPostalCodes.csv')
print(df)

FSA = set(df['FSA'].values.tolist())
print('M5V' in FSA)

with open('FSA.pickle', 'wb') as handle:
    pickle.dump(FSA, handle, protocol=pickle.HIGHEST_PROTOCOL)


df = pd.read_csv('canadacities.csv')
df['city'] = df['city'].str.lower()
df['postal'] = df['postal'].str.split()
print(df)

cities = set(df['city'].values.tolist())
print(cities)
with open('cities.pickle', 'wb') as handle:
    pickle.dump(cities, handle, protocol=pickle.HIGHEST_PROTOCOL)


cities_fsas = df[['city_ascii', 'postal']].values.tolist()
print(cities_fsas)

fsa_city_dict = {}
for city, fsas in cities_fsas:
    for fsa in fsas:
        fsa_city_dict[fsa] = city
print(fsa_city_dict)
with open('fsa-city-dict.pickle', 'wb') as handle:
    pickle.dump(fsa_city_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
