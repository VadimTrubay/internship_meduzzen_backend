FROM python:3.11

EXPOSE ${APP_PORT}

WORKDIR /APP

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host ${APP_HOST} --port ${APP_PORT}"]
