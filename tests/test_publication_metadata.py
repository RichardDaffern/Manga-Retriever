"""Offline tests: source-identity-locked manga metadata and cover-reference safety."""
from __future__ import annotations

import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from manga_retriever.publication_metadata import (
    SOURCE_TITLES,
    MetadataError,
    fetch_metadata,
    normalise,
)


def payload(slug: str, *, cover=True, status="completed") -> dict:
    fixed = SOURCE_TITLES[slug]
    relationships = [
        {"id": "11111111-1111-4111-8111-111111111111", "type": "author",
         "attributes": {"name": "Example Writer"}},
        {"id": "22222222-2222-4222-8222-222222222222", "type": "artist",
         "attributes": {"name": "Example Artist"}},
    ]
    if cover:
        relationships.append({
            "id": "33333333-3333-4333-8333-333333333333",
            "type": "cover_art", "attributes": {"fileName": "source-cover.jpg"},
        })
    return {
        "result": "ok",
        "data": {
            "id": fixed["sourceId"],
            "type": "manga",
            "attributes": {
                "title": {"en": fixed["name"]},
                "altTitles": [{"en": "Sample alternative English title"}],
                "description": {"en": "A short English synopsis", "ja": "Japanese summary"},
                "status": status,
                "tags": [
                    {"attributes": {"name": {"en": "Romance"}, "group": "genre"}},
                    {"attributes": {"name": {"en": "School Life"}, "group": "theme"}},
                    {"attributes": {"name": {"ja": "Missing English"}, "group": "genre"}},
                    {"attributes": {"name": {"en": "Award Winning"}, "group": "content"}},
                ],
            },
            "relationships": relationships,
        },
    }


class PublicationMetadataTests(unittest.TestCase):
    def test_all_five_pinned_titles_return_valid_review_candidates(self):
        self.assertEqual(len(SOURCE_TITLES), 5)
        for slug, record in SOURCE_TITLES.items():
            with self.subTest(slug=slug):
                out = normalise(slug, payload(slug), checked_at="2026-11-20T00:00:00+00:00")
                self.assertEqual(out["match"]["canonicalTitle"], record["name"])
                self.assertEqual(out["match"]["sourceMangaId"], record["sourceId"])
                self.assertEqual(out["metadata"]["creators"], ["Example Writer", "Example Artist"])
                self.assertEqual(out["metadata"]["tags"], ["Romance", "School Life"])
                self.assertEqual(out["metadata"]["synopsis"], "A short English synopsis")
                self.assertEqual(out["metadata"]["publicationStatus"], "completed")
                self.assertTrue(out["provenance"]["operatorReviewRequired"])
                self.assertFalse(out["provenance"]["replaceManualMetadata"])
                self.assertFalse(out["coverCandidate"]["assetDownloaded"])
                self.assertFalse(out["coverCandidate"]["rightsClearedForRedistribution"])
                self.assertNotIn("id", out["metadata"])
                self.assertNotIn("chapters", out["metadata"])

    def test_missing_metadata_remains_missing_not_fabricated(self):
        source = payload("last-game", cover=False, status="cancelled")
        attrs = source["data"]["attributes"]
        attrs["description"] = {"ja": "non English"}
        attrs["tags"] = []
        source["data"]["relationships"] = []
        output = normalise("last-game", source)
        self.assertEqual(output["metadata"]["creators"], [])
        self.assertIsNone(output["metadata"]["synopsis"])
        self.assertIsNone(output["coverCandidate"])
        self.assertEqual(output["metadata"]["publicationStatus"], "unknown")
        self.assertEqual(set(output["missing"]), {"creators", "synopsis", "tags", "cover"})

    def test_wrong_identity_and_unrelated_edition_fail_closed(self):
        for wrong_id in ("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "", None):
            doc = payload("relife")
            doc["data"]["id"] = wrong_id
            with self.assertRaises(MetadataError):
                normalise("relife", doc)
        doc = payload("relife")
        doc["data"]["attributes"]["title"] = {"en": "Entirely different manga"}
        doc["data"]["attributes"]["altTitles"] = []
        with self.assertRaises(MetadataError):
            normalise("relife", doc)

    def test_cover_invalid_filename_is_not_accepted(self):
        doc = payload("maid-sama")
        doc["data"]["relationships"][-1]["attributes"]["fileName"] = "../credentials.jpg"
        output = normalise("maid-sama", doc)
        self.assertIsNone(output["coverCandidate"])
        self.assertIn("cover", output["missing"])

    def test_author_and_artist_same_person_deduplicated(self):
        doc = payload("love-so-life")
        doc["data"]["relationships"][1]["attributes"]["name"] = "Example Writer"
        doc["data"]["relationships"][1]["id"] = doc["data"]["relationships"][0]["id"]
        out = normalise("love-so-life", doc)
        self.assertEqual(out["metadata"]["creators"], ["Example Writer"])
        self.assertEqual(len(out["metadata"]["creatorRoles"]), 2)

    def test_fixed_api_call_and_no_image_fetch(self):
        doc = payload("relife")
        raw = json.dumps(doc).encode()
        calls = []

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def geturl(self):
                return "https://api.mangadex.org/manga/" + SOURCE_TITLES["relife"]["sourceId"]

            def read(self, size):
                return raw

        def fake_open(request, *, timeout):
            calls.append(request.full_url)
            self.assertEqual(timeout, 20)
            return Response()

        record = fetch_metadata("relife", open_url=fake_open)
        self.assertTrue(record["coverCandidate"]["sourceUrl"].startswith("https://uploads.mangadex.org/"))
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].startswith(
            "https://api.mangadex.org/manga/" + SOURCE_TITLES["relife"]["sourceId"] + "?"
        ))
        self.assertIn("includes", calls[0])

    def test_api_redirect_and_oversized_data_rejected(self):
        doc = payload("relife")

        class Response:
            status = 200

            def __init__(self, url, data):
                self.url = url
                self.data = data

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def geturl(self):
                return self.url

            def read(self, _max):
                return self.data

        with self.assertRaises(MetadataError):
            fetch_metadata("relife", open_url=lambda *_a, **_k: Response(
                "https://example.org/unexpected", json.dumps(doc).encode()))
        with self.assertRaises(MetadataError):
            fetch_metadata("relife", open_url=lambda *_a, **_k: Response(
                "https://api.mangadex.org/manga/" + SOURCE_TITLES["relife"]["sourceId"],
                b"x" * 1_000_001))


if __name__ == "__main__":
    unittest.main()
