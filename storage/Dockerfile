FROM python:3-alpine

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps g++ gcc musl-dev postgresql-dev && \
 pip install -r requirements.txt && \
 apk --purge del .build-deps

ADD app/ /app

EXPOSE 8000

CMD ["python", "main.py"]
