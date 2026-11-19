"""One explicitly licensed Pepper&Carrot webcomic episode, not a generic scraper.

Episode 26 offers downloadable high-resolution, English rendered pages under
CC BY 4.0. Every page is discovered from that episode's official source page;
unknown hosts, redirects, formats, episodes and missing pages fail closed.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .importer import ImportFailure, import_local, verify_export

SOURCE_PAGE = "https://www.peppercarrot.com/en/webcomic-sources/ep26_Books-Are-Great.html"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
PAGE_PATH = re.compile(
    r"/0_sources/ep26_Books-Are-Great/hi-res/"
    r"en_Pepper-and-Carrot_by-David-Revoy_E26P(0[1-6])\.jpg"
)
REQUEST_TIMEOUT = 20
MAX_HTML_BYTES = 2_000_000
MAX_PAGE_BYTES = 25_000_000
EXPECTED_PAGE_COUNT = 6
TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class LicensedPage:
    number: int
    url: str


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href" and value)

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def _official_page_url(value: str) -> tuple[int, str] | None:
    url = urljoin(SOURCE_PAGE, value)
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != "www.peppercarrot.com"
            or parsed.username is not None or parsed.password is not None
            or parsed.port not in (None, 443) or parsed.query or parsed.fragment):
        return None
    match = PAGE_PATH.fullmatch(parsed.path)
    if not match:
        return None
    return int(match.group(1)), url


def plan_episode_26(html: bytes) -> tuple[LicensedPage, ...]:
    """Require the official licence and all six original high-resolution pages."""
    if not 0 < len(html) <= MAX_HTML_BYTES:
        raise ImportFailure("Source page is empty or oversized")
    parser = _Links()
    try:
        parser.feed(html.decode("utf-8"))
        parser.close()
    except (UnicodeDecodeError, ValueError) as error:
        raise ImportFailure("Cannot parse official episode source") from error
    def licensed_link(href: str) -> bool:
        parsed = urlsplit(urljoin(SOURCE_PAGE, href))
        return (parsed.scheme == "https" and parsed.hostname == "creativecommons.org"
                and parsed.username is None and parsed.password is None
                and parsed.port in (None, 443) and not parsed.query
                and parsed.path.rstrip("/") in
                ("/licenses/by/4.0", "/licenses/by/4.0/deed.en"))

    if not any(licensed_link(link) for link in parser.links):
        raise ImportFailure("Expected CC BY 4.0 licence link is missing")
    text = " ".join(parser.text)
    if "David Revoy" not in text or "Episode 26" not in text:
        raise ImportFailure("Official episode attribution is incomplete")
    pages: dict[int, str] = {}
    for href in parser.links:
        candidate = _official_page_url(href)
        if candidate is None:
            continue
        number, url = candidate
        if number in pages and pages[number] != url:
            raise ImportFailure("Conflicting episode page URLs")
        pages[number] = url
    if sorted(pages) != list(range(1, EXPECTED_PAGE_COUNT + 1)):
        raise ImportFailure("Incomplete licensed episode; refusing partial download")
    return tuple(LicensedPage(number, pages[number]) for number in sorted(pages))


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ImportFailure("Unexpected site redirect; refusing to follow it")


def _fetch(url: str, maximum: int) -> bytes:
    """Bounded GET for one constant official page or its strictly scoped image URLs."""
    if url != SOURCE_PAGE and _official_page_url(url) is None:
        raise ImportFailure("Unapproved web content URL")
    request = Request(url, headers={"User-Agent": "Taiyou-Manga-Retriever/0.1 (CC-BY-4.0)"})
    with build_opener(_NoRedirect).open(request, timeout=REQUEST_TIMEOUT) as response:
        if response.status != 200:
            raise ImportFailure("Source server returned unexpected status")
        if response.headers.get("Content-Length"):
            try:
                if int(response.headers["Content-Length"]) > maximum:
                    raise ImportFailure("Remote file exceeds byte limit")
            except ValueError as error:
                raise ImportFailure("Invalid source length header") from error
        content = response.read(maximum + 1)
        if not 0 < len(content) <= maximum:
            raise ImportFailure("Remote content empty or exceeds byte limit")
        return content


def fetch_with_retries(url: str, maximum: int, *, fetch=None, sleep=time.sleep) -> bytes:
    """Retry only transient HTTP/network problems with bounded backoff."""
    operation = fetch or _fetch
    for attempt in range(3):
        try:
            content = operation(url, maximum)
            if not isinstance(content, bytes) or not 0 < len(content) <= maximum:
                raise ImportFailure("Source returned invalid or oversized bytes")
            return content
        except HTTPError as error:
            if error.code not in TRANSIENT_STATUS or attempt == 2:
                raise ImportFailure(f"Source HTTP {error.code}, no further retry") from error
        except URLError as error:
            if attempt == 2:
                raise ImportFailure("Source network failure after bounded retries") from error
        sleep(2**attempt)
    raise ImportFailure("Source download failed")


def download_episode_26(output: Path, registry: Path, *, fetch=None, sleep=time.sleep) -> dict:
    """Download six licensed pages into a validated, private Controller-v1 export.

    Source artwork is never checked into this repository. The caller supplies a
    private destination; no automatic uploads or public GitHub artefacts occur.
    """
    if output.exists() or output.is_symlink():
        raise ImportFailure("Destination already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    html = fetch_with_retries(SOURCE_PAGE, MAX_HTML_BYTES, fetch=fetch, sleep=sleep)
    pages = plan_episode_26(html)
    work = Path(tempfile.mkdtemp(prefix=".peppercarrot-stage-", dir=output.parent))
    try:
        page_folder = work / "input" / "Pepper-and-Carrot" / "Episode 26"
        page_folder.mkdir(parents=True)
        for page in pages:
            data = fetch_with_retries(page.url, MAX_PAGE_BYTES, fetch=fetch, sleep=sleep)
            (page_folder / f"{page.number:04d}.jpg").write_bytes(data)
        rights = {
            "schemaVersion": 1,
            "sourceType": "licensed",
            "title": "Pepper&Carrot Episode 26: Books Are Great",
            "permissionEvidence": f"{SOURCE_PAGE} | {LICENCE_URL}",
            "attribution": (
                "Art/scenario: David Revoy; English contributors and all episode credits: "
                f"{SOURCE_PAGE}; CC BY 4.0: {LICENCE_URL}; original pages unmodified"
            ),
            "recordedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        rights_path = work / "rights.json"
        rights_path.write_text(json.dumps(rights, indent=2) + "\n", encoding="utf-8")
        staged = work / "completed"
        result = import_local(work / "input", staged, registry, rights_path=rights_path, direction="ltr")
        candidate = staged / "controller_candidate"
        catalogue = json.loads((candidate / "catalogue.json").read_text(encoding="utf-8"))
        chapter_id = catalogue[0]["chapters"][0]["id"]
        manifest = json.loads((candidate / "manifests" / f"{chapter_id}.json").read_text())
        records = [
            {
                "pageNumber": page.number,
                "sourceUrl": page.url,
                "assetPath": metadata["assetPath"],
                "sha256": metadata["sha256"],
            }
            for page, metadata in zip(pages, manifest["pages"], strict=True)
        ]
        summary_path = staged / "download_manifest.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["licensedSource"] = {
            "provider": "peppercarrot",
            "workType": "webcomic",
            "episode": 26,
            "language": "en",
            "sourcePage": SOURCE_PAGE,
            "licence": "CC BY 4.0",
            "licenceUrl": LICENCE_URL,
            "pages": records,
        }
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        if verify_export(staged) != result or len(records) != EXPECTED_PAGE_COUNT:
            raise ImportFailure("Downloaded episode failed final integrity verification")
        if output.exists() or output.is_symlink():
            raise ImportFailure("Destination appeared during download")
        staged.rename(output)
        return result
    finally:
        shutil.rmtree(work, ignore_errors=True)
