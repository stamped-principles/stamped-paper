FROM docker.io/library/python:3.14-slim-trixie

RUN apt-get update \
 && apt-get install -y --no-install-recommends make \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir PyYAML==6.0.3

WORKDIR /work
ENTRYPOINT ["make"]
