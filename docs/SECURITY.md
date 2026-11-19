# Security and media restrictions

Only trusted local files are accepted; this version has **no network requests**, eliminating HTTP SSRF/redirect exposure at this milestone. ZIP traversal, encrypted members, special entries, case-colliding member paths, suspicious compression ratio and quotas are rejected. Images are verified by Pillow, including magic format and full decode. Budgets are 25 MB/page, 1000 pages/chapter, 500 MB/chapter, 5 GB/import, 10,000 chapters/import, 16,000 pixels/side, 70 million pixels/image.

Input and output symlinks are rejected where checked. Local file race and filesystem capacity remain environmental threats; run imports only in trusted private folders. Outputs are not hosted, uploaded or auto-deleted. Git ignores media, registry and owner rights records. Do not assume Git ignore stops a manually forced git add.

Future network adapters must use explicit HTTPS host allowlists, DNS/rebinding and redirect validation, auth isolation, request/memory budgets, capped exponential backoff and documented publisher permission. Do not enable CI publication of copyrighted pages.

The Pepper&Carrot pilot accepts only the approved official Episode 26 source and six precise HTTPS high-resolution image paths on `www.peppercarrot.com`, with no credentials, arbitrary URLs or redirects. It rejects missing licence links, unrecognised hosts/paths, missing pages, corrupt images and incomplete exports. Retries are limited to selected transient HTTP codes and network failures.
