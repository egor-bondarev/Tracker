"""Exercise deployment and rollback against the disposable CI Compose project."""

import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import check_tracker

sys.modules["check_tracker"] = check_tracker
from deployment.acer import tracker_release as release


def container_id(name):
    return release.run(release.DOCKER + ["inspect", "--format", "{{.Id}}", name], capture=True).strip()


def main():
    # The CI workflow sets the same project name as Acer, but uses a fresh volume.
    database = container_id("tracker-tracker_database-1")
    with TemporaryDirectory() as temporary:
        release.CONFIG = Path(temporary)
        release.STATE = Path(temporary)
        shutil.copyfile("deployment/acer/compose.release.yml", release.CONFIG / "compose.yml")
        shutil.copyfile(".env", release.CONFIG / "tracker.env")

        baseline = release.load_state()["current"]
        candidate = {"revision": "ci-candidate", "images": {}}
        for component, image in baseline["images"].items():
            tag = f"tracker-ci-release-{component}:candidate"
            release.run(release.DOCKER + ["tag", image, tag])
            candidate["images"][component] = tag

        release.install_release(release.load_state(), candidate)
        assert release.load_state()["current"] == candidate
        assert container_id("tracker-tracker_database-1") == database

        broken = {
            "revision": "ci-bad-web",
            "images": candidate["images"] | {"web": candidate["images"]["record"]},
        }
        try:
            release.install_release(release.load_state(), broken)
        except RuntimeError as exc:
            assert "prior version is healthy again" in str(exc), str(exc)
        else:
            raise AssertionError("An unhealthy release was accepted.")
        assert release.load_state()["current"] == candidate

        release.install_release(release.load_state(), release.load_state()["previous"])
        assert release.load_state()["current"] == baseline
        assert container_id("tracker-tracker_database-1") == database
        assert "pending" not in json.loads((release.STATE / "releases.json").read_text())

    print("Release, failed-release recovery, and manual rollback passed.")


if __name__ == "__main__":
    main()
