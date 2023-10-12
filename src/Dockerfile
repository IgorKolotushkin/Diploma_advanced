FROM python:latest

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY . /src
COPY .env /

WORKDIR /

EXPOSE 8000

ENTRYPOINT ["uvicorn", "src.main:app_api", "--host", "0.0.0.0"]
