import base64
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
# import plotly.express as px
import pytz
from sqlalchemy.sql.expression import column
import streamlit as st
from sqlalchemy import create_engine

from io import StringIO
from dotenv import load_dotenv
load_dotenv(override=True)
from pathlib import Path
from streamlit import caching
from streamlit.report_thread import get_report_ctx
# caching.clear_cache()

ctx = get_report_ctx()

# @st.cache(allow_output_mutation=True)
def get_tweet_df():
    db_path = '/tmp/test.sqlite'
    engine = create_engine(f'sqlite:///{db_path}')
    tweet_df = pd.read_sql_table('tweet', engine)
    tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at'], utc=True)
    tweet_df = tweet_df.sort_values(by=['created_at'], ascending=False)
    tweet_df = tweet_df[tweet_df['created_at'] > datetime.now(timezone.utc) - timedelta(days=2)]
    # tweet_df = tweet_df.set_index('created_at')
    # tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at']) \
    #                          .dt.tz_localize('America/Toronto')
    return tweet_df

st.set_page_config('Vaccine Hunters', layout='wide')
st.title('Vaccine Hunters Search')
st.write("""
[Vaccine Hunters](https://vaccinehunters.ca/)

[Vaccine Hunters Twitter](https://twitter.com/vaxhunterscan?lang=en)
""")


tweet_df = get_tweet_df()

province = st.sidebar.selectbox(
    "Your province?",
    ("ON", "BC", "AB", "QC", "MB")
)

age_group = st.sidebar.selectbox(
    "Your age group?",
    ("18", "30", "40", "50",)
)
fsa = st.sidebar.text_input("FSA (First three characters of your postal code)")

st.sidebar.write("""
Contact: [riyad.parvez@gmail.com](riyad.parvez@gmail.com)

Hosting is sponsored by: [Ukko Agro](https://ukko.ag/)
""")

tweet_df = tweet_df[tweet_df['province'].str.contains(province, na=False, case=False)]
tweet_df = tweet_df[tweet_df['FSAs'].str.contains(fsa, na=False, case=False)]
tweet_df['tweet_text'] = tweet_df.apply(lambda row: f"[{row['tweet_text']}](https://twitter.com/twitter/statuses/{row['tweet_id']})", axis=1)
tweet_df = tweet_df[['created_at', 'tweet_text', 'province', 'age_groups', 'cities', 'FSAs',]]
tweet_df = tweet_df.rename(
    columns = {
        'created_at': 'Time',
        'tweet_text': 'Tweet',
        'province': 'Province',
        'age_groups': 'Age Groups',
        'cities': 'City',
        'FSAs': 'FSA',
    }
)
# tweet_df['Time'] = tweet_df['Time'].dt.strftime('%m-%d-%Y %h:%M')
tweet_df['Time'] = tweet_df['Time'].dt.strftime('%a %d %b %I:%M %p')
# st.write(tweet_df)
# st.write(tweet_df.to_markdown(tablefmt="grid"))
st.write(tweet_df.to_markdown(index=False))

