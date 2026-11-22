"""Offline safeguards for the five-title MangaDex metadata-only audit."""
from __future__ import annotations

import unittest

from scripts.new_target_mangadex_audit import TARGETS, audit_target, run_audit


def candidate(title="Love Hina", language="ja", manga_id="12345678-1234-4234-8234-123456789012"):
    return {
        "id": manga_id,
        "attributes": {
            "title": {language: title},
            "altTitles": [],
            "originalLanguage": "ja",
            "status": "completed",
        },
    }


class FakeClient:
    def __init__(self, *, selected=None, matches=None, chapters=None, manifest=None):
        self.selected = selected
        self.matches = matches if matches is not None else ([selected] if selected else [])
        self.chapters = chapters if chapters is not None else [
            {"id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
             "attributes": {"chapter": "1", "translatedLanguage": "en"}},
            {"id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
             "attributes": {"chapter": "2", "translatedLanguage": "en"}},
        ]
        self.manifest = manifest or {
            "status": "manifest-only-no-artwork-retrieved",
            "originalPagePaths": 18,
            "dataSaverPagePaths": 18,
        }
        self.feed_calls = []
        self.manifest_calls = []

    def discover(self, work):
        return self.selected, self.matches

    def feed(self, manga_id):
        self.feed_calls.append(manga_id)
        return len(self.chapters), self.chapters

    def image_manifest(self, chapter_id):
        self.manifest_calls.append(chapter_id)
        return self.manifest


class NewTargetMangaDexAuditTests(unittest.TestCase):
    def test_scope_contains_only_the_five_not_yet_audited_targets(self):
        self.assertEqual(
            [item["name"] for item in TARGETS],
            [
                "Kimi no Iru Machi",
                "Love Hina",
                "Lovely Complex",
                "Mado kara Madoka-chan",
                "The Fairytale-like You Goes on the Assault",
            ],
        )
        self.assertNotIn("Nisekoi", [item["name"] for item in TARGETS])

    def test_exact_match_reports_english_feed_and_manifest_without_media(self):
        selected = candidate(title="Love Hina", language="en")
        client = FakeClient(selected=selected)
        result = audit_target(TARGETS[1], client)
        self.assertEqual(result["mangaDexId"], selected["id"])
        self.assertEqual(result["englishFeedEntries"], 2)
        self.assertEqual(result["numberedCoverage"]["distinctNumberedChapters"], 2)
        self.assertEqual(result["sampleImageManifest"]["originalPagePaths"], 18)
        self.assertEqual(client.feed_calls, [selected["id"]])
        self.assertEqual(len(client.manifest_calls), 1)
        self.assertEqual(result["imageBytesDownloaded"], 0)
        self.assertEqual(result["cbzFilesCreated"], 0)
        self.assertFalse(result["rightsToArchiveOrRedistributeVerified"])
        self.assertFalse(result["eligibleForMediaDownload"])

    def test_no_exact_match_does_not_query_feed(self):
        client = FakeClient(selected=None, matches=[])
        result = audit_target(TARGETS[0], client)
        self.assertEqual(result["status"], "not-found")
        self.assertFalse(client.feed_calls)
        self.assertIsNone(result["englishFeedEntries"] if "englishFeedEntries" in result else None)

    def test_ambiguous_exact_editions_are_inspected_without_automatic_selection(self):
        first = candidate(title="Lovely★Complex")
        second = candidate(
            title="Lovely★Complex - Digital Colored Comics",
            manga_id="22222222-2222-4222-8222-222222222222",
        )
        client = FakeClient(selected=None, matches=[first, second])
        result = audit_target(TARGETS[2], client)
        self.assertEqual(result["status"], "ambiguous-exact-title")
        self.assertIsNone(result["mangaDexId"])
        self.assertEqual(len(result["candidateEditionAudits"]), 2)
        self.assertEqual(client.feed_calls, [first["id"], second["id"]])
        self.assertTrue(all(item["englishFeedEntries"] == 2 for item in result["candidateEditionAudits"]))
        self.assertTrue(all(not item["eligibleForMediaDownload"] for item in result["candidateEditionAudits"]))

    def test_feed_with_non_english_entry_fails_closed(self):
        selected = candidate()
        chapters = [
            {"id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
             "attributes": {"chapter": "1", "translatedLanguage": "en"}},
            {"id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
             "attributes": {"chapter": "2", "translatedLanguage": "ja"}},
        ]
        client = FakeClient(selected=selected, chapters=chapters)
        result = audit_target(TARGETS[1], client)
        self.assertEqual(result["status"], "source-check-failed")
        self.assertIn("not labelled English", result["error"])
        self.assertEqual(result["imageBytesDownloaded"], 0)

    def test_zero_original_paths_is_not_treated_as_working_image_source(self):
        selected = candidate()
        client = FakeClient(selected=selected, manifest={
            "status": "manifest-only-no-artwork-retrieved",
            "originalPagePaths": 0,
            "dataSaverPagePaths": 0,
        })
        result = audit_target(TARGETS[1], client)
        self.assertEqual(result["status"], "english-feed-without-hosted-original-pages")
        self.assertFalse(result["eligibleForMediaDownload"])

    def test_run_report_is_explicitly_metadata_only_and_rights_closed(self):
        class EmptyClient:
            def discover(self, work):
                return None, []
        report = run_audit(EmptyClient())
        self.assertEqual(report["totals"]["titlesChecked"], 5)
        self.assertEqual(report["totals"]["imageBytesDownloaded"], 0)
        self.assertEqual(report["totals"]["cbzFilesCreated"], 0)
        self.assertFalse(report["totals"]["rightsVerified"])
        self.assertFalse(any(item["mangaDexId"] for item in report["titles"]))


if __name__ == "__main__":
    unittest.main()
