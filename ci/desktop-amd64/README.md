# Desktop AMD64 image runner

This Ubuntu VM runs only trusted AMD64 image-publishing jobs. ARM64 jobs and tests keep their existing runners. QEMU runs with KVM inside a constrained Docker container. The VM has no desktop home mount or host Docker socket. GitHub administration credentials remain on the desktop; registration uses short-lived repository tokens.

The VM has 6 CPUs, 6 GiB RAM, and a 50 GiB sparse disk. A persistent BuildKit service has a 4 GiB memory limit and one active execution vertex. Compiler cache mounts survive job completion; garbage collection bounds retained builder data. A dedicated SSH key and disks live under `~/.local/share/desktop-ci`, outside this repository.

```sh
python3 ci/desktop-amd64/desktop-ci.py prepare
python3 ci/desktop-amd64/desktop-ci.py up
python3 ci/desktop-amd64/desktop-ci.py register daviddempsey/execution
install -Dm644 ci/desktop-amd64/desktop-ci.service ~/.config/systemd/user/desktop-ci.service
systemctl --user daemon-reload
systemctl --user enable --now desktop-ci.service
python3 ci/desktop-amd64/desktop-ci.py status
systemctl --user stop desktop-ci.service
```

Workflow image jobs use `runs-on: [self-hosted, Linux, X64, desktop-amd64]` and `docker/setup-buildx-action` with `driver: remote` and `endpoint: tcp://127.0.0.1:1234`. BuildKit is reachable only inside the VM. No QEMU action is necessary for native AMD64 jobs. Registration alone does not change routing.

The user service starts the VM with the desktop session. Stop it to pause desktop builds; AMD64 jobs then queue until it returns. Revert workflow routing before removing runners. Delete a repository runner through GitHub's runner settings before discarding its VM state. Never prune unrelated Docker data or mount the host socket into this VM.

Ubuntu image checksums and runner archive checksums are verified during setup. QEMU and BuildKit base images are pinned by digest. GitHub's runner updates itself normally. Guest OS updates and pinned image updates require a controlled restart when no jobs are active.
