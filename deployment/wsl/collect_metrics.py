"""Write a small dashboard snapshot using Docker and /proc/meminfo."""

import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


STATE = Path("/var/lib/homelab-metrics")
WINDOWS_SNAPSHOT = Path("/mnt/c/ProgramData/AcerHomelab/metrics/windows.json")
CONTAINER_FORMAT = (
    '{"name":{{json .Names}},"state":{{json .State}},'
    '"status":{{json .Status}},"project":{{json (.Label "com.docker.compose.project")}}}'
)


def docker_lines(*args):
    result = subprocess.run(
        ["/usr/bin/docker", *args], check=True, capture_output=True, text=True, timeout=12,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line]


def memory():
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        name, _, value = line.partition(":")
        if name in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
            values[name] = int(value.split()[0]) * 1024
    return {
        "total_bytes": values["MemTotal"],
        "available_bytes": values["MemAvailable"],
        "swap_total_bytes": values["SwapTotal"],
        "swap_used_bytes": values["SwapTotal"] - values["SwapFree"],
    }


def projects():
    containers = docker_lines("ps", "-a", "--format", CONTAINER_FORMAT)
    stats = {}
    if any(container["state"] == "running" for container in containers):
        stats = {
            row["Name"]: row
            for row in docker_lines("stats", "--no-stream", "--format", "{{json .}}")
        }
    by_project = {}
    for container in sorted(containers, key=lambda item: item["name"]):
        name = container["name"]
        sample = stats.get(name, {}) if container["state"] == "running" else {}
        project = container["project"] or None
        by_project.setdefault(project, []).append({
            "name": name,
            "state": container["state"],
            "status": container["status"],
            "cpu": sample.get("CPUPerc"),
            "memory": sample["MemUsage"].split(" / ", 1)[0] if "MemUsage" in sample else None,
        })
    return [
        {"name": project, "containers": by_project[project]}
        for project in sorted(by_project, key=lambda name: (name is None, name or ""))
    ]


def write_snapshot(target, data):
    data["collected_at"] = datetime.now(timezone.utc).isoformat()
    with tempfile.NamedTemporaryFile(mode="w", dir=STATE, delete=False) as file:
        path = Path(file.name)
        try:
            json.dump(data, file)
            file.flush()
            os.fchmod(file.fileno(), 0o644)
            path.replace(STATE / f"{target}.json")
        finally:
            path.unlink(missing_ok=True)


def refresh_windows():
    previous = WINDOWS_SNAPSHOT.stat().st_mtime_ns if WINDOWS_SNAPSHOT.exists() else 0
    subprocess.run(
        ["/mnt/c/Windows/System32/schtasks.exe", "/Run", "/TN", "Acer-HostMetrics"],
        check=True, capture_output=True, timeout=8, cwd="/mnt/c/Windows",
    )
    for _ in range(24):
        if WINDOWS_SNAPSHOT.exists() and WINDOWS_SNAPSHOT.stat().st_mtime_ns > previous:
            return
        time.sleep(0.5)
    raise TimeoutError("Windows snapshot did not advance")


def main():
    target = sys.stdin.buffer.readline(32).strip()
    if target not in {b"windows", b"wsl", b"docker"}:
        print("error", flush=True)
        return
    name = target.decode("ascii")
    try:
        with (STATE / f"{name}.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if name == "windows":
                refresh_windows()
            elif name == "wsl":
                write_snapshot(name, {"memory": memory()})
            else:
                write_snapshot(name, {"projects": projects()})
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        print(f"Metrics refresh failed for {name}: {type(exc).__name__}", file=sys.stderr)
        print("error", flush=True)
        return
    print("ok", flush=True)


if __name__ == "__main__":
    main()
