"""Regression guard: historic third-party media must not be published by public CI.

This deliberately checks only the retired job gates, not unrelated licensed
Pepper&Carrot workflows or metadata-only source investigation workflows.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOW_DIR = Path(__file__).resolve().parents[1] / ".github" / "workflows"
QUARANTINED = {
    "relife-series.yml": ("download",),
    "relife-download.yml": ("download",),
    "love-so-life-download.yml": ("verified-chapter-batches",),
    "love-so-life-extras-download.yml": ("verify-five-extras",),
    "three-manga-download.yml": ("download-and-verify",),
    "onizuka-recovery-download.yml": ("download-onizuka",),
    "kainushi-available-download.yml": ("verified-partial-source-batches",),
    "relife-auto-recovery.yml": ("retry-failed",),
    "three-manga-recovery.yml": ("automatic-retry",),
    "additional-manga-recovery.yml": ("retry-failed",),
}
JOB_PATTERN = re.compile(r"^  ([A-Za-z0-9_-]+):[ \t]*$", re.MULTILINE)
DISABLED = re.compile(r"^    if: \$\{\{ false \}\}[ \t]*$", re.MULTILINE)


class QuarantinedMediaWorkflowsTests(unittest.TestCase):
    def test_all_legacy_public_media_jobs_are_disabled(self):
        for name, targets in QUARANTINED.items():
            with self.subTest(workflow=name):
                path = WORKFLOW_DIR / name
                source = path.read_text(encoding="utf-8")
                blocks = list(JOB_PATTERN.finditer(source))
                jobs = {}
                for index, match in enumerate(blocks):
                    # Only top-level YAML job keys are indented by exactly two spaces.
                    end = blocks[index + 1].start() if index + 1 < len(blocks) else len(source)
                    jobs[match.group(1)] = source[match.end():end]
                for job in targets:
                    with self.subTest(job=job):
                        self.assertIn(job, jobs)
                        self.assertRegex(jobs[job], DISABLED)

    def test_creator_licensed_workflows_remain_usable(self):
        for name in ("bulk-manga.yml", "download-manga.yml"):
            with self.subTest(workflow=name):
                source = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
                self.assertNotRegex(source, DISABLED)
                self.assertIn("peppercarrot", source.lower())


if __name__ == "__main__":
    unittest.main()
