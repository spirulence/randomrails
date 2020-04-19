FROM node:12-slim as frontend-builder

WORKDIR /app

COPY ./frontend /app

RUN yarn install
RUN yarn run build --prefix-paths

FROM python:3.8-slim

WORKDIR /app

COPY ./backend /app

RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev && pip install pipenv && pipenv install --deploy --system

COPY --from=frontend-builder /app/public /app/crayonrails/game/static

WORKDIR /app/crayonrails

RUN SECRET_KEY=secretforstatic PRODUCTION_STATICFILES=true python manage.py collectstatic

CMD python manage.py migrate && gunicorn crayonrails.wsgi
