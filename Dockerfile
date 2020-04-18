FROM node:12-slim as frontend-builder

WORKDIR /app

COPY ./frontend /app

RUN yarn install
RUN yarn run build

FROM python:3.8-slim

WORKDIR /app

COPY ./backend /app

RUN pip install pipenv && pipenv install --deploy --system

COPY --from=frontend-builder /app/public /app/crayonrails/game/static

WORKDIR /app/crayonrails

CMD python manage.py migrate && gunicorn crayonrails.wsgi