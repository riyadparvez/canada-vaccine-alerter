from datetime import datetime, timezone, timedelta
from loguru import logger

def search_tweet_df(tweet_df, search_criteria):
    is_search_expanded = False

    filtered_tweet_df = tweet_df
    province = search_criteria['province']
    age_group = search_criteria['age_group']
    fsa = search_criteria['fsa']
    city = search_criteria['city']
    keyword = search_criteria['keyword']

    if province != 'ALL':
        filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['province'].str.contains(province, na=False, case=False)]
        search_criteria['province'] = province

    if age_group != 'ANY':
        search_substr = age_group
        if age_group == '30+':
            search_substr = '18|30'
        elif age_group == '40+':
            search_substr = '18|30|40'
        elif age_group == '50+':
            search_substr = '18|30|40|50'
        filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['age_groups'].str.contains(search_substr, na=False, case=False)]
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

    if filtered_tweet_df.empty:
        search_substr = '|'.join([val for val in search_criteria.values()])
        logger.info(f"Expanding search criteria 'keyword': {search_substr}")
        filtered_tweet_df = tweet_df[tweet_df['tweet_text'].str.contains(search_substr, na=False, case=False)]
        mask = filtered_tweet_df['province'].str.contains(province, na=False, case=False) | filtered_tweet_df['province'].isnull()
        filtered_tweet_df = filtered_tweet_df[mask]
        filtered_tweet_df = filtered_tweet_df.sort_values(by=['province', 'created_at',])
        logger.warning(f"No results have been found for: {search_criteria}. Expanded search criteria.")
        is_search_expanded = True

    if len(search_criteria) > 20:
        filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=3))]
    else:
        filtered_tweet_df = filtered_tweet_df[filtered_tweet_df['created_at'] > (datetime.now(timezone.utc) - timedelta(days=7))]

    return filtered_tweet_df, is_search_expanded
