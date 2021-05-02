from config import DB_PATH
from db import tweets, page_views
from datetime import datetime, timedelta, timezone
import json
import pandas as pd
import SessionState
import streamlit as st

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from bokeh.plotting import figure
# from bokeh.models import ColumnDataSource, CustomJS
# from bokeh.models import DataTable, TableColumn, HTMLTemplateFormatter
from dotenv import load_dotenv
load_dotenv(override=True)
from loguru import logger
from streamlit.report_thread import get_report_ctx
from telegram.utils.helpers import escape_markdown

report_ctx = get_report_ctx()

province_index_dict = {
    "ALL": 0,
    "ON": 1,
    "BC": 2,
    "AB": 3,
    "QC": 4,
    "MB": 5,
    "SK": 6,
    "NB": 7,
    "NS": 8,
    "PEI": 9,
}

age_group_index_dict = {
    "ANY": 0,
    "18+": 1,
    "30+": 2,
    "40+": 3,
    "50+": 4,
}

@st.cache(ttl=60)
def get_tweet_df():
    logger.info(f"Reading Tweets from sqlite database")
    engine = create_engine(f'sqlite:///{DB_PATH}')
    tweet_df = pd.read_sql_table('tweet', engine)
    tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at'], utc=True)
    tweet_df = tweet_df.sort_values(by=['created_at'], ascending=False)
    # tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at']) \
    #                          .dt.tz_localize('America/Toronto')
    logger.info(f"Retrieved {len(tweet_df)} tweets")
    return tweet_df

def insert_page_view(session_id, search_criteria):
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    search_criteria_str = json.dumps(search_criteria)
    with Session() as session:
        ins = page_views.insert().values(
            session_id=session_id,
            search_criteria=search_criteria_str,
            )
        res = session.execute(ins)
        session.commit()

logger.info(f"Serving session: {get_report_ctx().session_id}")

session_state = SessionState.get(province='ALL', age_group='ANY', city='', fsa='', keyword='',)

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

refresh = st.sidebar.button("Refresh Results")

province = st.sidebar.selectbox(
    "Your province?",
    ("ALL", "ON", "BC", "AB", "QC", "MB", "SK", "NB", "NS", "PEI",),
)

age_group = st.sidebar.selectbox(
    "Your age group?",
    ("ANY", "18+", "30+", "40+", "50+",),
)

city = st.sidebar.text_input("City or Region (Please ensure it's correct spelling)")
fsa = st.sidebar.text_input("FSA (First three characters of your postal code)")
keyword = st.sidebar.text_input("Any specific keyword (eg pregnant, immuno-compromised)")

session_state.age_group = age_group
session_state.province = province
session_state.city = city
session_state.fsa = fsa
session_state.keyword = keyword

st.sidebar.write("""
Contact: [riyad.parvez@gmail.com](riyad.parvez@gmail.com)

Source Code: [Github Repo](https://github.com/riyadparvez/canada-vaccine-alerter)

Hosting is sponsored by: [Ukko Agro](https://ukko.ag/)
""")

search_criteria = {}
filtered_tweet_df = tweet_df
if province != 'ALL':
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['province'].str.contains(province, na=False, case=False)]
    search_criteria['province'] = province
if age_group != 'ANY':
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['age_groups'].str.contains(age_group, na=False, case=False)]
    search_criteria['age_group'] = age_group
if len(fsa) > 0:
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['FSAs'].str.contains(fsa, na=False, case=False)]
    search_criteria['fsa'] = fsa
if len(city) > 0:
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['cities'].str.contains(city, na=False, case=False)]
    search_criteria['city'] = city
if len(keyword) > 0:
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['tweet_text'].str.contains(keyword, na=False, case=False)]
    search_criteria['keyword'] = keyword

insert_page_view(report_ctx.session_id, search_criteria)

if filtered_tweet_df.empty:
    search_substr = '|'.join([val for val in search_criteria.values()])
    logger.info(f"Expanding search criteria 'keyword': {search_substr}")
    filtered_tweet_df = tweet_df[tweet_df['tweet_text'].str.contains(search_substr, na=False, case=False)]
    st.warning("""
    #### We have expanded your search criteria to find more matches.
    """)

if len(search_criteria) > 0:
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=1))]
else:
    filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=3))]

if not filtered_tweet_df.empty:
    logger.info(f"{len(filtered_tweet_df)} results found for: {search_criteria}")
    # tweet_df['tweet_text'] = tweet_df.apply(lambda row: f"{row['tweet_text']}\nLink: (https://twitter.com/twitter/statuses/{row['tweet_id']})", axis=1)
    filtered_tweet_df = filtered_tweet_df.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n',  ' ', regex=True)
    # tweet_df['tweet_text'] = tweet_df['tweet_text'].map(lambda x: escape_markdown(x, version=2))
    filtered_tweet_df['tweet_text'] = filtered_tweet_df.apply(lambda row: f"[{escape_markdown(row['tweet_text'], version=2)}](https://twitter.com/twitter/statuses/{row['tweet_id']})", axis=1)
    filtered_tweet_df['tweet_link'] = filtered_tweet_df['tweet_id'].map(lambda x: f"https://twitter.com/twitter/statuses/{x}")
    filtered_tweet_df['cities'] = filtered_tweet_df['cities'].str.slice(1,-1)
    filtered_tweet_df['cities'] = filtered_tweet_df['cities'].str.replace(r"'", '')
    filtered_tweet_df['FSAs'] = filtered_tweet_df['FSAs'].str.slice(1,-1)
    filtered_tweet_df['FSAs'] = filtered_tweet_df['FSAs'].str.replace(r"'", '')
    filtered_tweet_df['age_groups'] = filtered_tweet_df['age_groups'].str.slice(1,-1)

    filtered_tweet_df = filtered_tweet_df[['created_at', 'tweet_text', 'province', 'age_groups', 'cities', 'FSAs',]]
    filtered_tweet_df = filtered_tweet_df.rename(
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
    filtered_tweet_df['Time'] = filtered_tweet_df['Time'].dt.tz_convert('US/Eastern')
    filtered_tweet_df['Time'] = filtered_tweet_df['Time'].dt.strftime('%a %d %b %I:%M %p')
    # st.write(filtered_tweet_df.to_markdown(tablefmt="grid"))

    st.write(filtered_tweet_df.to_markdown(index=False))
else:
    logger.info(f"No Results found for: {search_criteria}")
    st.warning("""
    #### We couldn't find any tweets from Vaccine Hunters in your search criteria. It is still possible that you are eligible for vaccination.
    #### Please try searching on internet or try again later.
    """)

# tweet_df = tweet_df.set_index('Time')
# st.table(tweet_df)

# TERMS of USE and PRIVACY POLICY
if False:
    st.markdown("""
    <style>
    .small-font {
        font-size:10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="small-font">Hello World !!</p>', unsafe_allow_html=True)
