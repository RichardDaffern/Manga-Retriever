"""Offline end-to-end recovery tests against authorised source adapter, using invented pages."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

from PIL import Image

from manga_retriever.importer import ImportFailure, verify_export
from manga_retriever.peppercarrot import LICENCE_URL, SOURCE_PAGE, download_episode_26

PAGE_ROOT = (
    "https://www.peppercarrot.com/0_sources/ep26_Books-Are-Great/hi-res/"
    "en_Pepper-and-Carrot_by-David-Revoy_E26P"
)


def html() -> bytes:
    links = "".join(f'<a href="{PAGE_ROOT}{n:02d}.jpg">Page {n}</a>' for n in range(1, 7))
    return f'<h1>Episode 26: Books Are Great</h1><div>David Revoy</div><a href="{LICENCE_URL}">CC BY 4.0</a>{links}'.encode()


def jpeg(i: int) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (16, 16), (i * 30, 15, 25)).save(stream, format="JPEG")
    return stream.getvalue()


class M4PepperCarrotTests(unittest.TestCase):
    def test_interruption_preserves_only_verified_pages_then_resumes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            output = base / "ep26"
            registry = base / "ids.json"
            requests = []
            interrupted = True

            def fetch(url: str, maximum: int) -> bytes:
                requests.append(url)
                if url == SOURCE_PAGE:
                    return html()
                if interrupted and url == PAGE_ROOT + "04.jpg":
                    raise HTTPError(url, 503, "offline", None, None)
                number = int(url[-6:-4])
                return jpeg(number)

            with self.assertRaises(ImportFailure):
                download_episode_26(output, registry, fetch=fetch, sleep=lambda _: None)
            self.assertFalse(output.exists())
            self.assertFalse(registry.exists())
            checkpoint = base / ".ep26.checkpoint"
            state = json.loads((checkpoint / "checkpoint.json").read_text())
            self.assertEqual(sorted(state["completed"]), ["0001.jpg", "0002.jpg", "0003.jpg"])
            interrupted = False
            requests.clear()
            self.assertEqual(
                download_episode_26(output, registry, fetch=fetch, sleep=lambda _: None),
                {"series": 1, "chapters": 1, "pages": 6},
            )
            self.assertEqual(verify_export(output)["pages"], 6)
            self.assertEqual(requests, [SOURCE_PAGE] + [PAGE_ROOT + f"{n:02d}.jpg" for n in range(4, 7)])
            self.assertFalse(checkpoint.exists())

    def test_corrupted_checkpoint_page_is_retrieved_again(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            output = base / "episode"
            fail = True
            calls = []

            def fetch(url: str, maximum: int) -> bytes:
                calls.append(url)
                if url == SOURCE_PAGE:
                    return html()
                if fail and url == PAGE_ROOT + "03.jpg":
                    raise HTTPError(url, 404, "permanent", None, None)
                return jpeg(int(url[-6:-4]))

            with self.assertRaises(ImportFailure):
                download_episode_26(output, base / "ids.json", fetch=fetch, sleep=lambda _: None)
            page1 = base / ".episode.checkpoint" / "pages" / "0001.jpg"
            page1.write_bytes(b"corrupt")
            fail = False
            calls.clear()
            self.assertEqual(download_episode_26(output, base / "ids.json", fetch=fetch, sleep=lambda _: None)["pages"], 6)
            self.assertIn(PAGE_ROOT + "01.jpg", calls)
            self.assertNotIn(PAGE_ROOT + "02.jpg", calls)


if __name__ == "__main__":
    unittest.main()
