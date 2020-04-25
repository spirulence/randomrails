FROM python:3.8-slim as geos-builder

RUN apt-get update && apt-get install -y git build-essential cmake git

RUN git clone --depth 1 https://github.com/libgeos/geos.git /geos-master

WORKDIR /geos-master

RUN mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/geos-install .. \
    && make -j 2 && ctest . && make install

FROM scratch

COPY --from=geos-builder /geos-install /geos-install