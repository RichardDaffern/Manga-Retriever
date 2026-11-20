"""Offline tests for a deliberately metadata-only third-party catalogue integration."""
from __future__ import annotations

import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from scripts.five_manga_catalogue import (
    SOURCES,
    CatalogueError,
    list_with_client,
    summarise,
)


def listing(slug: str, count: int, *, extra=None) -> dict:
    return {
        "title": SOURCES[slug]["title"],
        "grabber": "PlainHTML",
        "chapters": [{"number": x, "title": f"Chapter {x}"} for x in range(1, count + 1)] + (extra or []),
        "languages": None,
        "scanlators": None,
        "volumes": "",
    }


class FiveMangaCatalogueTests(unittest.TestCase):
    def test_fixed_exact_source_urls(self):
        self.assertEqual(len(SOURCES), 5)
        for slug, source in SOURCES.items():
            with self.subTest(slug=slug):
                self.assertTrue(source["url"].startswith("https://mangakatana.com/manga/"))
                self.assertTrue(source["expectedMain"] > 0)

    def test_all_five_complete_numbered_catalogues_are_only_metadata(self):
        for slug, source in SOURCES.items():
            with self.subTest(slug=slug):
                report = summarise(slug, listing(slug, source["expectedMain"]))
                self.assertEqual(report["catalogueStatus"], "complete-numbered-metadata")
                self.assertEqual(report["missingMainChapters"], [])
                self.assertFalse(report["downloadOrRedistributionRightsVerified"])
                self.assertFalse(report["englishTranslationVerified"])
                self.assertFalse(report["imageFidelityVerified"])
                self.assertEqual(report["archivesCreated"], 0)

    def test_missing_chapter_is_not_silently_accepted(self):
        source = listing("love-hina", 120)
        source["chapters"] = [c for c in source["chapters"] if c["number"] != 4]
        summary = summarise("love-hina", source)
        self.assertEqual(summary["catalogueStatus"], "partial-or-uncertain-metadata")
        self.assertEqual(summary["missingMainChapters"], [4])

    def test_decimal_extras_do_not_substitute_for_missing_chapters(self):
        source = listing("lovely-complex", 65, extra=[{"number": 65.5, "title": "Bonus"}])
        summary = summarise("lovely-complex", source)
        self.assertEqual(summary["missingMainChapters"], [66])
        self.assertEqual(summary["decimalLabels"], ["65.5"])

    def test_chapter_zero_extra_does_not_count_as_main_or_invalid(self):
        source = listing("nisekoi", 229, extra=[{"number": 0, "title": "One-shot"}])
        summary = summarise("nisekoi", source)
        self.assertEqual(summary["chapterZeroExtras"], 1)
        self.assertEqual(summary["invalidEntries"], 0)
        self.assertEqual(summary["distinctExpectedMain"], 229)
        self.assertEqual(summary["catalogueStatus"], "complete-numbered-metadata")

    def test_wrong_series_never_marked_complete(self):
        source = listing("nisekoi", 229)
        source["title"] = "Nisekoi Fake Edition"
        summary = summarise("nisekoi", source)
        self.assertEqual(summary["catalogueStatus"], "review-title-mismatch")

    def test_locked_chapter_prevents_complete_status(self):
        source = listing("mado-kara-madoka-chan", 74)
        source["chapters"][0]["locked"] = True
        summary = summarise("mado-kara-madoka-chan", source)
        self.assertEqual(summary["lockedEntries"], 1)
        self.assertNotEqual(summary["catalogueStatus"], "complete-numbered-metadata")

    def test_boolean_nan_and_out_of_bounds_are_invalid(self):
        source = listing("lovely-complex", 66)
        source["chapters"].extend([{"number": True}, {"number": float("nan")}, {"number": -3}])
        summary = summarise("lovely-complex", source)
        self.assertEqual(summary["invalidEntries"], 3)
        self.assertNotEqual(summary["catalogueStatus"], "complete-numbered-metadata")

    def test_client_invoked_only_with_list_and_exact_url(self):
        raw = json.dumps(listing("love-hina", 120)).encode()
        runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=raw))
        report = list_with_client("love-hina", "/trusted/manga-downloader", run=runner)
        self.assertEqual(report["distinctExpectedMain"], 120)
        args, kwargs = runner.call_args
        self.assertEqual(args[0], [
            "/trusted/manga-downloader", "list", "--json",
            "https://mangakatana.com/manga/love-hina.4545",
        ])
        self.assertFalse(kwargs["check"])
        self.assertTrue(kwargs["capture_output"])
        self.assertNotIn("shell", kwargs)

    def test_invalid_slug_or_corrupt_response_rejected(self):
        runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=b"not json"))
        with self.assertRaises(CatalogueError):
            list_with_client("another-manga", "client", run=runner)
        runner.assert_not_called()
        with self.assertRaises(CatalogueError):
            list_with_client("nisekoi", "client", run=runner)

    def test_site_error_fails_closed(self):
        runner = Mock(return_value=SimpleNamespace(returncode=22, stdout=b""))
        with self.assertRaises(CatalogueError):
            list_with_client("nisekoi", "client", run=runner)

    def test_invalid_listing_schema_fails_closed(self):
        with self.assertRaises(CatalogueError):
            summarise("love-hina", {"title": "Love Hina", "chapters": []})
        with self.assertRaises(CatalogueError):
            summarise("love-hina", {"title": "Love Hina", "chapters": ["invalid"] * 1501})


if __name__ == "__main__":
    unittest.main()
