import sys
import unittest
from unittest.mock import patch

from scripts import check_tracker

# The Acer installer places the shared check next to the release controller.
with patch.dict(sys.modules, {"check_tracker": check_tracker}):
    from deployment.acer import tracker_release as release


SHA = "a" * 40
DIGESTS = ["sha256:" + c * 64 for c in ("b", "c", "d")]
CANDIDATE = release.release_for(SHA, DIGESTS)
CURRENT = {"revision": "pre-automation", "images": {"web": "tracker-local-web:fixture"}}


class AcerReleaseTests(unittest.TestCase):
    def test_user_input_cannot_select_arbitrary_images(self):
        for revision, images in [
            ("main", DIGESTS),
            (SHA, ["docker.io/other/image:latest", *DIGESTS[1:]]),
            (SHA, DIGESTS[:2]),
        ]:
            with self.subTest(revision=revision, images=images):
                with self.assertRaises(ValueError):
                    release.release_for(revision, images)
        self.assertTrue(CANDIDATE["images"]["web"].startswith("ghcr.io/egor-bondarev/tracker-web@"))

    @patch.object(release, "write_state")
    @patch.object(release, "apply")
    @patch.object(release, "run")
    @patch.object(release, "require_current_main", side_effect=ValueError("main moved"))
    @patch.object(release, "prepare")
    def test_stale_automatic_release_does_not_touch_containers(self, prepare, guard, run, apply, state):
        with self.assertRaisesRegex(ValueError, "main moved"):
            release.install_release({"current": CURRENT, "previous": None}, CANDIDATE, auto=True)
        apply.assert_not_called()
        state.assert_not_called()

    @patch.object(release, "write_state")
    @patch.object(release, "apply", side_effect=[RuntimeError("unhealthy"), None])
    @patch.object(release, "run")
    @patch.object(release, "prepare")
    def test_failed_deploy_restores_healthy_release(self, prepare, run, apply, write):
        prior = {"current": CURRENT, "previous": None}
        with self.assertRaisesRegex(RuntimeError, "prior version is healthy"):
            release.install_release(prior, CANDIDATE)
        self.assertEqual([call.args[0] for call in apply.call_args_list], [CANDIDATE, CURRENT])
        self.assertEqual(write.call_args_list[0].args[0], {**prior, "pending": CANDIDATE})
        self.assertEqual(write.call_args_list[1].args[0], prior)

    @patch.object(release, "write_state")
    @patch.object(release, "apply")
    @patch.object(release, "run")
    @patch.object(release, "prepare")
    def test_manual_rollback_swaps_healthy_release_slots(self, prepare, run, apply, write):
        release.install_release({"current": CANDIDATE, "previous": CURRENT}, CURRENT)
        apply.assert_called_once_with(CURRENT)
        self.assertEqual(write.call_args.args[0], {"current": CURRENT, "previous": CANDIDATE})
