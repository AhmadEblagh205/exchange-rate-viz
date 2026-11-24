"""Download the ECB euro reference exchange-rate history.

Source: European Central Bank, https://www.ecb.europa.eu/stats/eurofxref/

Default behaviour reuses the local snapshot (and says so). `--refresh`
replaces it and writes data/raw/eurofxref-hist.manifest.json holding the
source URL, the UTC retrieval time and the SHA-256 of the CSV.
"""
import argparse
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_zip(url: str) -> bytes:
    """Default network fetch; tests inject a fake instead."""
    with urlopen(url, timeout=60) as resp:
        return resp.read()


def extract_csv(zip_bytes: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".csv"))
        return zf.read(name)


def download(raw_dir=RAW, refresh=False, fetch=fetch_zip, url=URL, now=None) -> Path:
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "eurofxref-hist.csv"
    if csv_path.exists() and not refresh:
        print(f"Reusing the local snapshot (not refreshed): {csv_path}")
        print("Run with --refresh to download the current ECB file.")
        return csv_path
    print("Downloading from the ECB...")
    data = extract_csv(fetch(url))
    csv_path.write_bytes(data)
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    manifest = {"source_url": url,
                "retrieved_utc": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data)}
    (raw_dir / "eurofxref-hist.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(f"Saved -> {csv_path} (manifest written)")
    return csv_path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true",
                    help="replace the local snapshot and write a manifest")
    download(refresh=ap.parse_args().refresh)


if __name__ == "__main__":
    main()
