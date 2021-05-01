FROM python:3.7-slim

ARG SQLALCHEMY_DATABASE_URI=""

ENV AWS_REGION us-east-1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install --yes git openssh-client
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
# RUN git clone git@github.com:riyadparvez/canada-vaccine-alerter.git

RUN pip3 install pipenv && pip3 install --upgrade setuptools

COPY Pipfile* /usr/src/app/
RUN pipenv install --dev --deploy --system
# RUN sed -i 's/ \\xb7 Streamlit//g' /usr/local/lib/python3.7/site-packages/streamlit/static/static/js/main.68bdddd4.chunk.js
# RUN pipenv run python -m spacy download en_core_web_trf
# RUN pipenv run python -m nltk.downloader punkt

COPY . /usr/src/app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
