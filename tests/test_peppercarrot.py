"""Offline synthetic tests: no live web requests or copyrighted pages."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

from PIL import Image

from manga_retriever.importer import ImportFailure, verify_export
from manga_retriever.peppercarrot import (
    LICENCE_URL,
    SOURCE_PAGE,
    _official_page_url,
    download_episode_26,
    fetch_with_retries,
    plan_episode_26,
)


PAGE_ROOT = (
    "https://www.peppercarrot.com/0_sources/ep26_Books-Are-Great/hi-res/"
    "en_Pepper-and-Carrot_by-David-Revoy_E26P"
)


def sample_html(numbers=range(1, 7), *, licensed=True) -> bytes:
    links = ''.join(f'<a href="{PAGE_ROOT}{n:02d}.jpg">Illustration and text</a>' for n in numbers)
    licence = f'<a href="{LICENCE_URL}">Creative Commons Attribution 4.0</a>' if licensed else ''
    return f'<h1>Episode 26: Books Are Great</h1><div>David Revoy</div>{licence}{links}'.encode()


def jpeg(rgb: tuple[int, int, int]) -> bytes:
    content = io.BytesIO()
    Image.new('RGB', (16, 18), rgb).save(content, format='JPEG')
    return content.getvalue()


class PepperCarrotTests(unittest.TestCase):
    def test_discovers_six_high_resolution_pages(self) -> None:
        pages = plan_episode_26(sample_html())
        self.assertEqual([p.number for p in pages], [1, 2, 3, 4, 5, 6])
        self.assertTrue(all('hi-res' in page.url for page in pages))

    def test_incomplete_source_fails_closed(self) -> None:
        with self.assertRaises(ImportFailure):
            plan_episode_26(sample_html(numbers=range(1, 6)))

    def test_missing_licence_fails_closed(self) -> None:
        with self.assertRaises(ImportFailure):
            plan_episode_26(sample_html(licensed=False))

    def test_bad_host_and_path_are_not_approved(self) -> None:
        self.assertIsNone(_official_page_url('https://www.peppercarrot.com.evil.test/0_sources/a'))
        self.assertIsNone(_official_page_url(PAGE_ROOT + '01.jpg?access=1'))
        self.assertIsNone(_official_page_url(PAGE_ROOT.replace('hi-res', 'low-res') + '01.jpg'))

    def test_permanent_http_error_not_retried(self) -> None:
        requested = []

        def fetch(url: str, size: int) -> bytes:
            requested.append(url)
            raise HTTPError(url, 404, "not found", None, None)

        with self.assertRaises(ImportFailure):
            fetch_with_retries(SOURCE_PAGE, 500, fetch=fetch, sleep=lambda _: None)
        self.assertEqual(requested, [SOURCE_PAGE])

    def test_transient_http_error_retried(self) -> None:
        attempts = []
        delays = []

        def fetch(url: str, size: int) -> bytes:
            attempts.append(1)
            if len(attempts) < 3:
                raise HTTPError(url, 503, "unavailable", None, None)
            return b'ok'

        self.assertEqual(fetch_with_retries(SOURCE_PAGE, 500, fetch=fetch, sleep=delays.append), b'ok')
        self.assertEqual(len(attempts), 3)
        self.assertEqual(delays, [1, 2])

    def test_download_creates_verified_attributed_export(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            outputs = {}
            for page in range(1, 7):
                outputs[f'{PAGE_ROOT}{page:02d}.jpg'] = jpeg((page * 20, 20, 20))

            requested = []

            def fetch(url: str, maximum: int) -> bytes:
                requested.append(url)
                if url == SOURCE_PAGE:
                    return sample_html()
                return outputs[url]

            output = base / 'episode-26'
            registry = base / 'ids.json'
            result = download_episode_26(output, registry, fetch=fetch, sleep=lambda _: None)
            self.assertEqual(result, {'series': 1, 'chapters': 1, 'pages': 6})
            self.assertEqual(verify_export(output), result)
            rights = json.loads((output / 'controller_candidate' / 'rights.json').read_text())
            self.assertIn('creativecommons.org/licenses/by/4.0', rights['permissionEvidence'])
            source = json.loads((output / 'download_manifest.json').read_text())['licensedSource']
            self.assertEqual(source['workType'], 'webcomic')
            self.assertEqual(source['licence'], 'CC BY 4.0')
            self.assertEqual(len(source['pages']), 6)
            self.assertEqual(requested, [SOURCE_PAGE, *outputs.keys()])
            self.assertEqual(download_episode_26.__name__, 'download_episode_26')
            with self.assertRaises(ImportFailure):
                download_episode_26(output, registry, fetch=fetch)

    def test_failed_episode_never_publishes_partial_export(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / 'episode-26'

            def fetch(url: str, maximum: int) -> bytes:
                if url == SOURCE_PAGE:
                    return sample_html()
                if url.endswith('E26P04.jpg'):
                    raise HTTPError(url, 404, 'missing', None, None)
                return jpeg((50, 60, 70))

            with self.assertRaises(ImportFailure):
                download_episode_26(output, root / 'ids.json', fetch=fetch, sleep=lambda _: None)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
