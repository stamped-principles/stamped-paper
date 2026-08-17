# Build environment for the manuscript PDF.
# ubuntu:24.04 with the same TeX Live packages CI previously installed on the
# ubuntu-latest runner, so the rendered PDF is unchanged.
FROM docker.io/library/ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      make \
      latex-make \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-latex-extra \
      texlive-fonts-recommended \
      texlive-bibtex-extra \
      python3 \
      python3-yaml \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
