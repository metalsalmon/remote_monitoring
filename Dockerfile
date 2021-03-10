
ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}-buster

RUN pip install pipenv

COPY . /backend
WORKDIR /backend

RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT FLASK_APP=/backend/app.py FLASK_ENV=development flask run --host=0.0.0.0