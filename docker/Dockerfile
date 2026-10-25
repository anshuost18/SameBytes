FROM debian:unstable
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/debian.sources || true
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential devscripts dpkg-dev fakeroot equivs reprotest diffoscope \
    disorderfs ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
