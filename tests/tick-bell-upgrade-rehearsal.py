#!/usr/bin/env python3
"""Rehearse a Tick & Bell package upgrade and rollback in disposable Debian arm64."""
import argparse
from hashlib import sha256
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def version(deb):
    assert run("dpkg-deb", "-f", deb, "Package") == "tick-bell"
    assert run("dpkg-deb", "-f", deb, "Architecture") == "arm64"
    return run("dpkg-deb", "-f", deb, "Version")


def install(deb, downgrade=False):
    plan = run("apt-get", "-s", *("--allow-downgrades",) if downgrade else (), "install", deb)
    changes = [line.split()[:2] for line in plan.splitlines()
               if line.startswith(("Inst ", "Remv "))]
    assert changes == [["Inst", "tick-bell"]], changes
    subprocess.run(["dpkg", "--force-confold", "--install", deb], check=True)
    assert run("dpkg-query", "-W", "-f=${Version}", "tick-bell") == version(deb)


def digest(file):
    return sha256(file.read_bytes()).hexdigest()


def request(path, command):
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(2)
        client.connect(str(path))
        client.sendall(command.encode() + b"\n")
        with client.makefile() as response:
            return response.read()


class Scheduler:
    binary = Path("/usr/bin/tick-bell-scheduler")

    def __init__(self, root):
        self.sock = root / "clock.sock"
        self.env = dict(os.environ, TICKBELL_SOCKET=str(self.sock),
                        XDG_STATE_HOME=str(root / "state"), HOME=str(root))
        self.proc = None

    def __enter__(self):
        self.proc = subprocess.Popen([self.binary], env=self.env)
        try:
            until = time.monotonic() + 8
            while time.monotonic() < until and self.proc.poll() is None:
                try:
                    if request(self.sock, "SNAP"):
                        executable = Path(f"/proc/{self.proc.pid}/exe")
                        assert executable.resolve() == self.binary
                        assert digest(executable) == digest(self.binary)
                        return self
                except OSError:
                    pass
                time.sleep(.05)
            raise RuntimeError("Fixture scheduler did not start")
        except BaseException:
            self.__exit__()
            raise

    def __exit__(self, *_):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=5)

    def send(self, command):
        return request(self.sock, command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=lambda p: str(Path(p).resolve()))
    parser.add_argument("new", type=lambda p: str(Path(p).resolve()))
    opts = parser.parse_args()
    if not Path("/.dockerenv").exists() or os.geteuid() != 0 or run("dpkg", "--print-architecture") != "arm64":
        parser.error("Run only as root inside a disposable Debian arm64 Docker container")
    if subprocess.run(["dpkg-query", "-W", "tick-bell"], capture_output=True).returncode == 0:
        parser.error("Use a fresh container without Tick & Bell installed")
    subprocess.run(["dpkg", "--compare-versions", version(opts.old), "lt", version(opts.new)], check=True)
    with tempfile.TemporaryDirectory(prefix="tb-upgrade-") as directory:
        root = Path(directory)
        state = root / "state/tick-bell/state"
        backup = root / "state.before"
        install(opts.old)
        with Scheduler(root) as service:
            assert service.send("ACREATE\t7\t30\t0\t0\tCHIME\t9\t-\tExample alarm") == "OK\n"
            original = service.send("SNAP")
            alarm = next(line.split("\t") for line in original.splitlines() if line.startswith("A\t"))
            assert alarm[2:9] == ["7", "30", "0", "0", "CHIME", "9", "IDLE"]
            assert alarm[-1] == "Example alarm"
        shutil.copy2(state, backup)
        baseline = digest(backup)

        install(opts.new)
        with Scheduler(root) as service:
            assert service.send("SNAP") == original
        assert digest(state) == baseline
        print(f"Upgrade {version(opts.old)} → {version(opts.new)} kept the alarm and state bytes.", flush=True)

        install(opts.old, downgrade=True)
        with Scheduler(root) as service:
            assert service.send("SNAP") == original
            assert service.send(f"ADELETE\t{alarm[1]}") == "OK\n"
            assert service.send("SNAP") != original
        shutil.copy2(state, root / "state.after")
        replacement = state.with_name("state.recovery")
        shutil.copy2(backup, replacement)
        replacement.replace(state)
        with Scheduler(root) as service:
            assert service.send("SNAP") == original
        assert digest(state) == baseline
        print("Rollback kept the alarm; recovery also restored it in the deliberately changed fixture.")


if __name__ == "__main__":
    main()
