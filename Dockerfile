FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py
ENV DEBUG True

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .

RUN cat requirements.txt

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir simphile

COPY env.sample .env

COPY . .

RUN ./install_nlpdb.sh

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
