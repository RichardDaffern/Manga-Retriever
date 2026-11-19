"""Metadata-only audit of ReLIFE GitHub Actions batch artefact coverage."""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

BATCHES = [(s, min(s + 19, 222)) for s in range(1, 223, 20)]
EXPECTED = [f"ReLIFE-Original-Quality-Ch{s}-{e}" for s, e in BATCHES]


def summarise(run_id: int, attempt: int, conclusion: str, data: dict) -> dict:
    if type(run_id) is not int or run_id <= 0 or type(attempt) is not int or attempt <= 0:
        raise ValueError("Invalid source run or attempt")
    if conclusion not in {"success", "failure", "cancelled", "timed_out", "neutral", "skipped"}:
        raise ValueError("Invalid source conclusion")
    if not isinstance(data, dict) or not isinstance(data.get("artifacts"), list):
        raise ValueError("Malformed GitHub artefact listing")
    names = set()
    for entry in data["artifacts"]:
        if not isinstance(entry, dict):
            raise ValueError("Malformed GitHub artefact item")
        if isinstance(entry.get("name"), str) and not entry.get("expired"):
            names.add(entry["name"])
    expected = set(EXPECTED)
    present = [name for name in EXPECTED if name in names]
    missing = [name for name in EXPECTED if name not in names]
    return {
        "schemaVersion": 1,
        "sourceRun": run_id,
        "sourceAttempt": attempt,
        "sourceConclusion": conclusion,
        "checkedUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expectedBatches": len(expected),
        "availableBatches": len(present),
        "availableArtifactNames": present,
        "missingOrExpiredArtifactNames": missing,
        "allTwelveAvailable": not missing,
        "caveat": "A verified CBZ artefact does not prove distinct publisher chapter identity or publisher-original resolution.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--conclusion", required=True)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    data = json.loads(opts.artifacts.read_text(encoding="utf-8"))
    report = summarise(opts.run_id, opts.attempt, opts.conclusion, data)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ReLIFE batch artefacts available: {report['availableBatches']}/12")
    print("Missing/expired:", report["missingOrExpiredArtifactNames"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
