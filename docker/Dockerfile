# samebytes-builder: Debian unstable toolchain for twin builds (see docs/VERIFICATION_HARNESS.md)
# Build:  docker build -t samebytes-builder:2026-10-25 -f docker/Dockerfile docker/
FROM debian:unstable@sha256:ac638695600796dac818dd0a79ef04147649eca20368daaf3add2ab7a0e08ae0

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8

# deb-src is required for `apt-get source` and `apt-get build-dep`.
# apt fetches over plain HTTP got random 400s from one CDN edge, so switch to HTTPS after bootstrapping ca-certificates.
RUN printf 'Acquire::Retries "5";\n' > /etc/apt/apt.conf.d/99samebytes \
 && sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/debian.sources \
 && apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && sed -i 's#http://#https://#g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential devscripts dpkg-dev fakeroot quilt equivs \
      faketime locales-all tzdata \
      diffoscope-minimal binutils file xz-utils zstd unzip \
      ripgrep git python3 \
      reprotest disorderfs \
 && rm -rf /var/lib/apt/lists/*

# Build users mirroring tests.reproducible-builds.org (build A = pbuilder1, build B = pbuilder2).
# Home directories deliberately do not exist.
RUN groupadd -g 1111 pbuilder1 \
 && useradd -u 1111 -g 1111 -M -d /nonexistent/first-build -s /bin/sh \
      -c "first user,first room,first work-phone,first home-phone,first other" pbuilder1 \
 && groupadd -g 2222 pbuilder2 \
 && useradd -u 2222 -g 2222 -M -d /nonexistent/second-build -s /bin/bash \
      -c "second user,second room,second work-phone,second home-phone,second other" pbuilder2

COPY sb-build /usr/local/bin/sb-build
RUN chmod 0755 /usr/local/bin/sb-build && mkdir -p /build/reproducible-path /out /src

WORKDIR /build
