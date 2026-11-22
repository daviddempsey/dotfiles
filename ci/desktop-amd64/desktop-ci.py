#!/usr/bin/env python3
"""Manage a native desktop CI VM without installing host packages."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
import urllib.request

SOURCE = Path(__file__).resolve().parent
STATE = Path.home() / ".local/share/desktop-ci"
ENV = dict(os.environ, DESKTOP_CI_STATE=str(STATE),
           DESKTOP_CI_UID=str(os.getuid()), DESKTOP_CI_GID=str(os.getgid()))
COMPOSE = ["docker", "compose", "-f", str(SOURCE / "compose.yaml")]
SSH = ["ssh", "-p", "2227", "-i", str(STATE / "id_ed25519"),
       "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
       "-o", "StrictHostKeyChecking=accept-new", "-o", f"UserKnownHostsFile={STATE}/known_hosts",
       "root@127.0.0.1"]


def run(command, **kwargs):
    return subprocess.run(command, check=True, env=ENV, **kwargs)


def api(path, method="GET"):
    return json.loads(run(["gh", "api", "--method", method, path], capture_output=True, text=True).stdout)


def image_tool(*args):
    return run(["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
                "-v", f"{STATE}:/vm", "--entrypoint", args[0], "local/desktop-ci-vm:1", *args[1:]])


def prepare():
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    run([*COMPOSE, "build"])
    if not (STATE / "id_ed25519").exists():
        run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "desktop-ci-only",
             "-f", str(STATE / "id_ed25519")], stdout=subprocess.DEVNULL)
    base = STATE / "base.img"
    if not base.exists():
        url = "https://cloud-images.ubuntu.com/noble/current/"
        filename = "noble-server-cloudimg-amd64.img"
        checksums = urllib.request.urlopen(url + "SHA256SUMS").read().decode()
        expected = next(s.split()[0] for s in checksums.splitlines() if s.split()[-1].lstrip("*") == filename)
        partial = STATE / "base.img.partial"
        print("Downloading the official Ubuntu AMD64 cloud image", flush=True)
        urllib.request.urlretrieve(url + filename, partial)
        with partial.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise SystemExit("Ubuntu image checksum mismatch")
        partial.rename(base)
        (STATE / "base.sha256").write_text(actual + "\n")
    if not (STATE / "system.qcow2").exists():
        image_tool("qemu-img", "create", "-f", "qcow2", "-F", "qcow2", "-b", "/vm/base.img", "/vm/system.qcow2", "50G")
    public_key = (STATE / "id_ed25519.pub").read_text().strip()
    userdata = (SOURCE / "cloud-init.yaml").read_text().replace("__SSH_PUBLIC_KEY__", public_key)
    (STATE / "user-data").write_text(userdata)
    (STATE / "meta-data").write_text("instance-id: desktop-ci-v1\nlocal-hostname: desktop-ci\n")
    if not (STATE / "seed.img").exists():
        image_tool("cloud-localds", "/vm/seed.img", "/vm/user-data", "/vm/meta-data")


def up():
    run([*COMPOSE, "up", "-d"])
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        try:
            result = subprocess.run([*SSH, "cloud-init status --wait"], env=ENV,
                                    capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            continue
        if result.returncode == 0:
            print(result.stdout.strip())
            return
        time.sleep(3)
    raise SystemExit(f"VM boot timed out; inspect {STATE}/console.log")


def register(repo):
    if not re.fullmatch(r"daviddempsey/[a-zA-Z0-9_.-]+", repo):
        raise SystemExit("Expected a daviddempsey repository")
    metadata = api(f"repos/{repo}")
    print(f"Registering an image-only runner for {repo} (private={metadata['private']})", flush=True)
    archive = next(item for item in api(f"repos/{repo}/actions/runners/downloads")
                   if item["os"] == "linux" and item["architecture"] == "x64")
    token = api(f"repos/{repo}/actions/runners/registration-token", "POST")["token"]
    payload = dict(archive, repo=repo, token=token)
    run(["scp", "-P", "2227", "-i", str(STATE / "id_ed25519"),
         "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
         "-o", f"UserKnownHostsFile={STATE}/known_hosts", str(SOURCE / "register-runner.py"),
         "root@127.0.0.1:/usr/local/bin/register-desktop-runner"], stdout=subprocess.DEVNULL)
    run([*SSH, "python3 /usr/local/bin/register-desktop-runner"], input=json.dumps(payload), text=True)


def stop():
    try:
        with socket.socket(socket.AF_UNIX) as connection:
            connection.settimeout(3)
            connection.connect(str(STATE / "qmp.sock"))
            stream = connection.makefile("rwb", buffering=0)
            stream.readline()
            stream.write(b'{"execute":"qmp_capabilities"}\n')
            stream.readline()
            stream.write(b'{"execute":"system_powerdown"}\n')
        for _ in range(60):
            if not (STATE / "qmp.sock").exists():
                break
            time.sleep(1)
    except (OSError, TimeoutError):
        pass
    run([*COMPOSE, "stop"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "up", "register", "ssh", "status", "stop"])
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "up":
        up()
    elif args.command == "register":
        for repo in args.args:
            register(repo)
    elif args.command == "ssh":
        run([*SSH, *args.args])
    elif args.command == "status":
        run([*COMPOSE, "ps"])
        run([*SSH, "uname -m; systemctl --no-pager --plain list-units 'desktop-*'"])
    else:
        stop()


if __name__ == "__main__":
    main()
