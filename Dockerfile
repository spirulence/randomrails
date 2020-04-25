FROM node:12-slim as frontend-builder

WORKDIR /app

COPY ./frontend /app

RUN yarn install
RUN yarn run build --prefix-paths

FROM spirulence/python-libgeos as geos-builder

FROM python:3.8-slim

WORKDIR /app

COPY ./backend /app
COPY --from=geos-builder /geos-install /usr/

RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev git \
    && pip install cython==0.29.16 numpy==1.18.3 pipenv \
    && pipenv install --deploy --system \
    && pip install -e git+https://github.com/Toblerity/Shapely.git@de4838e102dcfd54aadc8af03ed33def918334e6#egg=shapely

COPY --from=frontend-builder /app/public /app/crayonrails/game/static

WORKDIR /app/crayonrails

RUN SECRET_KEY=secretforstatic PRODUCTION_STATICFILES=true python manage.py collectstatic

CMD python manage.py migrate && gunicorn crayonrails.wsgi
