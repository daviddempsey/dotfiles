#!/usr/bin/env python3
"""Run inside the CI VM; registration input arrives only on stdin."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys
import tarfile
import urllib.request

data = json.load(sys.stdin)
repo = data["repo"]
if not re.fullmatch(r"daviddempsey/[a-zA-Z0-9_.-]+", repo):
    raise SystemExit("Unsupported repository")
name = repo.split("/", 1)[1]
directory = Path("/srv/actions") / name
directory.mkdir(parents=True, exist_ok=True)
if (directory / ".runner").exists():
    print(f"{repo}: already registered")
    raise SystemExit(0)
archive = Path("/var/cache") / data["filename"]
if not archive.exists():
    urllib.request.urlretrieve(data["download_url"], archive)
if hashlib.file_digest(archive.open("rb"), "sha256").hexdigest() != data["sha256_checksum"]:
    raise SystemExit("Runner archive checksum mismatch")
with tarfile.open(archive) as runner:
    runner.extractall(directory, filter="data")
account = pwd.getpwnam("ci-runner")
subprocess.run(["chown", "-R", f"{account.pw_uid}:{account.pw_gid}", str(directory)], check=True)
env = os.environ.copy()
env["ACTIONS_RUNNER_INPUT_TOKEN"] = data.pop("token")
env["HOME"] = account.pw_dir
subprocess.run([
    "runuser", "-u", "ci-runner", "--", "./config.sh", "--unattended",
    "--url", f"https://github.com/{repo}", "--name", f"desktop-amd64-{name}",
    "--labels", "desktop-amd64,image-builder", "--work", "_work",
], cwd=directory, env=env, check=True)
subprocess.run(["systemctl", "enable", "--now", f"desktop-runner@{name}"], check=True)
print(f"{repo}: runner service enabled")
