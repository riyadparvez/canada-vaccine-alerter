## Vaccine Updates

This the source code repo of [vaccineupdates.ca](vaccineupdates.ca) site.

### Getting Started
* sqlite is used as database. This is the sql for `tweet` table
```sql
CREATE TABLE tweet (
	id INTEGER NOT NULL, 
	tweet_id INTEGER, 
	tweet_text VARCHAR, 
	province VARCHAR, 
	age_groups VARCHAR, 
	cities VARCHAR, 
	"FSAs" VARCHAR, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	ingested_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	UNIQUE (tweet_id)
);
```
* [litestream](https://litestream.io) is used to back up sqlite db to s3
* Please create a `config.yml` similar to below

```python
DB_PATH = 'paths-to-db.sqlite'

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
```
and fill up necessary secrets to run the app.
* Build docker image: `docker build -t vax-searcher .`
* Run the batch sync `docker run vax-searcher python stream_sync.py -d 3`. `-d 3` means last three days tweets will be synced and processed.
* Run the real-time sync `docker run vax-searcher python batch_sync.py`. This will use Twitter streaming API to sync tweets in real-time.
