FROM debian:trixie-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      diff-pdf-wx \
      xvfb \
      xauth \
      x11-utils \
      poppler-utils \
      imagemagick \
      fontconfig \
      fonts-dejavu-core \
      curl \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /work
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
