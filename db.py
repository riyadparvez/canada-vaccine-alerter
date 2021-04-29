from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, func

meta = MetaData()

tweets = Table(
   'tweet', meta, 
   Column('id', Integer, primary_key = True), 
   Column('tweet_id', Integer, unique=True), 
   Column('tweet_text', String), 
   Column('province', String), 
   Column('age_groups', String), 
   Column('cities', String), 
   Column('FSAs', String), 
   Column('created_at', DateTime(timezone=True), server_default=func.now()),
   Column('ingested_at', DateTime(timezone=True), server_default=func.now()),
)

db_path = '/tmp/test.sqlite'
engine = create_engine(f'sqlite:///{db_path}')
meta.create_all(engine)

Session = sessionmaker(bind=engine)
