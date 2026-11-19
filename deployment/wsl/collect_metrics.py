"""Write a small dashboard snapshot using Docker and /proc/meminfo."""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SNAPSHOT = Path("/var/lib/homelab-metrics/wsl.json")
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


def main():
    data = {"memory": memory(), "projects": None}
    try:
        data["projects"] = projects()
    except (subprocess.SubprocessError, OSError, ValueError):
        # A daemon failure must not hide WSL memory or look like an empty container list.
        print("Could not collect Docker metrics.", flush=True)
    data["collected_at"] = datetime.now(timezone.utc).isoformat()
    with tempfile.NamedTemporaryFile(mode="w", dir=SNAPSHOT.parent, delete=False) as file:
        path = Path(file.name)
        try:
            json.dump(data, file)
            file.flush()
            os.fchmod(file.fileno(), 0o644)
            path.replace(SNAPSHOT)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
