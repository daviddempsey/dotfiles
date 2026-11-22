FROM ubuntu:24.04@sha256:9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289
RUN apt-get update && apt-get install -y --no-install-recommends \
    qemu-system-x86 qemu-utils cloud-image-utils ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY start-vm.sh /usr/local/bin/start-vm
ENTRYPOINT ["/bin/sh", "/usr/local/bin/start-vm"]
