import base64
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
# import plotly.express as px
import pytz
import streamlit as st

from sqlalchemy.sql.expression import column
from sqlalchemy import create_engine, log
# from bokeh.plotting import figure
# from bokeh.models import ColumnDataSource, CustomJS
# from bokeh.models import DataTable, TableColumn, HTMLTemplateFormatter
from io import StringIO
from dotenv import load_dotenv
load_dotenv(override=True)
from loguru import logger
from pathlib import Path
from streamlit import caching
from streamlit.report_thread import get_report_ctx
from telegram.utils.helpers import escape_markdown

ctx = get_report_ctx()

def get_tweet_df():
    db_path = '/tmp/test.sqlite'
    engine = create_engine(f'sqlite:///{db_path}')
    tweet_df = pd.read_sql_table('tweet', engine)
    tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at'], utc=True)
    tweet_df = tweet_df.sort_values(by=['created_at'], ascending=False)
    # tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at']) \
    #                          .dt.tz_localize('America/Toronto')
    return tweet_df

logger.info(f"Serving session: {get_report_ctx().session_id}")

st.set_page_config(page_title='Vaccine Updates', layout='wide')
st.title('Vaccine Hunters Search')
st.write("""
### This website lets you search Vaccine Hunters tweets by province, age group and postal code.

[Vaccine Hunters](https://vaccinehunters.ca/)

[Vaccine Hunters Twitter](https://twitter.com/vaxhunterscan?lang=en)

""")

with st.beta_expander("Official Vaccine Sites:"):
    st.write("""
* [Canada Govt. Vaccine Site](https://www.canada.ca/en/public-health/services/diseases/coronavirus-disease-covid-19/vaccines.html)
* [Ontario Vaccine Site](https://covid-19.ontario.ca/book-vaccine/)
* [British Columbia Vaccine Site](https://www2.gov.bc.ca/gov/content/covid-19/vaccine/plan)
* [Quebec Vaccine Site](https://www.quebec.ca/en/health/health-issues/a-z/2019-coronavirus/progress-of-the-covid-19-vaccination)
* [Alberta Vaccine Site](https://www.alberta.ca/covid19-vaccine.aspx)
* [Manitoba Vaccine Site](https://www.gov.mb.ca/covid19/vaccine/index.html)
* [Saskatchewan Vaccine Site](https://www.saskatchewan.ca/covid19-vaccine)
* [Nova Scotia Vaccine Site](https://novascotia.ca/coronavirus/book-your-vaccination-appointment/)
* [New Brunswick Vaccine Site](https://www2.gnb.ca/content/gnb/en/corporate/promo/covid-19/nb-vaccine.html)
* [PEI Vaccine Site](https://www.princeedwardisland.ca/en/information/health-and-wellness/getting-covid-19-vaccine)
    """)

tweet_df = get_tweet_df()

province = st.sidebar.selectbox(
    "Your province?",
    ("ALL", "ON", "BC", "AB", "QC", "MB")
)

age_group = st.sidebar.selectbox(
    "Your age group?",
    ("ANY", "18", "30", "40", "50",)
)

city = st.sidebar.text_input("City or Region (Please ensure it's correct spelling)")

fsa = st.sidebar.text_input("FSA (First three characters of your postal code)")

keyword = st.sidebar.text_input("Any specific keyword (eg pregnant, immuno-compromised)")

st.sidebar.write("""
Contact: [riyad.parvez@gmail.com](riyad.parvez@gmail.com)

[Github Repo](https://github.com/riyadparvez/canada-vaccine-alerter)

Hosting is sponsored by: [Ukko Agro](https://ukko.ag/)
""")

is_search_criteria = False

if province != 'ALL':
    tweet_df = tweet_df[tweet_df['province'].str.contains(province, na=False, case=False)]
    is_search_criteria= True
if age_group != 'ANY':
    tweet_df = tweet_df[tweet_df['age_groups'].str.contains(age_group, na=False, case=False)]
    is_search_criteria= True
if len(fsa) > 0:
    tweet_df = tweet_df[tweet_df['FSAs'].str.contains(fsa, na=False, case=False)]
    is_search_criteria= True
if len(city) > 0:
    tweet_df = tweet_df[tweet_df['cities'].str.contains(city, na=False, case=False)]
    is_search_criteria= True
if len(keyword) > 0:
    tweet_df = tweet_df[tweet_df['tweet_text'].str.contains(keyword, na=False, case=False)]
    is_search_criteria= True

if not is_search_criteria:
    tweet_df = tweet_df[tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=1))]
else:
    tweet_df = tweet_df[tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=3))]

if not tweet_df.empty:
    # tweet_df['tweet_text'] = tweet_df.apply(lambda row: f"{row['tweet_text']}\nLink: (https://twitter.com/twitter/statuses/{row['tweet_id']})", axis=1)
    tweet_df = tweet_df.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n',  ' ', regex=True)
    # tweet_df['tweet_text'] = tweet_df['tweet_text'].map(lambda x: escape_markdown(x, version=2))
    tweet_df['tweet_text'] = tweet_df.apply(lambda row: f"[{escape_markdown(row['tweet_text'], version=2)}](https://twitter.com/twitter/statuses/{row['tweet_id']})", axis=1)
    tweet_df['tweet_link'] = tweet_df['tweet_id'].map(lambda x: f"https://twitter.com/twitter/statuses/{x}")
    # tweet_df = tweet_df[['created_at', 'tweet_text', 'province', 'tweet_link', 'age_groups', 'cities', 'FSAs',]]

    tweet_df = tweet_df[['created_at', 'tweet_text', 'province', 'age_groups', 'cities', 'FSAs',]]
    tweet_df = tweet_df.rename(
        columns = {
            'created_at': 'Time',
            'tweet_text': 'Tweet',
            'tweet_link': 'Link',
            'province': 'Province',
            'age_groups': 'Age Groups',
            'cities': 'City',
            'FSAs': 'FSA',
        }
    )
    # tweet_df['Time'] = tweet_df['Time'].dt.strftime('%m-%d-%Y %h:%M')
    tweet_df['Time'] = tweet_df['Time'].dt.tz_convert('US/Eastern')
    tweet_df['Time'] = tweet_df['Time'].dt.strftime('%a %d %b %I:%M %p')
    # st.write(tweet_df)
    # st.write(tweet_df.to_markdown(tablefmt="grid"))

    st.write(tweet_df.to_markdown(index=False))
else:
    st.write("""
    #### We couldn't find any tweets from Vaccine Hunters in your search criteria. It is still possible that you are eligible for vaccination.
    #### Please try searching on internet or try again later.
    """)

# tweet_df = tweet_df.set_index('Time')
# st.table(tweet_df)


# cds = ColumnDataSource(tweet_df)
# columns = [
#     TableColumn(field="tweet_link", title="Link", formatter=HTMLTemplateFormatter(template='<a href="<%= value %>"target="_blank"><%= value %>')),
# ]
# p = DataTable(source=cds, columns=columns, css_classes=["my_table"])
# st.bokeh_chart(p)
