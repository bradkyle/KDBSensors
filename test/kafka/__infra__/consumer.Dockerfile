FROM python:3.8-slim-buster
COPY consumer.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD python consumer.py