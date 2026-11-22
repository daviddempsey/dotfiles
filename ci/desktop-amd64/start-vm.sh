#!/bin/sh
set -eu
exec qemu-system-x86_64 \
  -enable-kvm -cpu host -smp 6 -m 6144 \
  -machine q35 -display none -no-reboot \
  -drive file=/vm/system.qcow2,if=virtio,format=qcow2,discard=unmap \
  -drive file=/vm/seed.img,if=virtio,format=raw,readonly=on \
  -netdev user,id=net0,hostfwd=tcp:0.0.0.0:2222-:22 \
  -device virtio-net-pci,netdev=net0 \
  -device virtio-rng-pci \
  -serial file:/vm/console.log \
  -qmp unix:/vm/qmp.sock,server=on,wait=off
