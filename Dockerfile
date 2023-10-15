FROM python:latest

ADD src/requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY src /app/src
COPY src/.env /app/
COPY alembic /app/alembic
COPY alembic.ini /app

RUN chmod a+x app/src/docker/*.sh
WORKDIR /

EXPOSE 8000

#ENTRYPOINT ["uvicorn", "src.main:app_api", "--host", "0.0.0.0"]
