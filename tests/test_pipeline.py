import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone

import pytest

from audit import run_audit, write_sample
from download_data import download
from visualize import generate_all

CSV = b"Date,USD\n2020-01-02,1.1\n"


def fake_zip(payload=CSV):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("eurofxref-hist.csv", payload)
    return buf.getvalue()


def test_cache_reuse_does_not_fetch(tmp_path, capsys):
    (tmp_path / "eurofxref-hist.csv").write_bytes(b"cached")

    def boom(url):
        raise AssertionError("network must not be used")

    path = download(tmp_path, fetch=boom)
    assert path.read_bytes() == b"cached"
    assert "Reusing the local snapshot" in capsys.readouterr().out
    assert not (tmp_path / "eurofxref-hist.manifest.json").exists()


def test_refresh_replaces_file_and_writes_manifest(tmp_path):
    (tmp_path / "eurofxref-hist.csv").write_bytes(b"old")
    now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    download(tmp_path, refresh=True, fetch=lambda url: fake_zip(), now=now)
    assert (tmp_path / "eurofxref-hist.csv").read_bytes() == CSV
    m = json.loads((tmp_path / "eurofxref-hist.manifest.json").read_text())
    assert m["sha256"] == hashlib.sha256(CSV).hexdigest()
    assert m["retrieved_utc"] == "2026-01-02T03:04:05Z"
    assert m["source_url"].startswith("https://www.ecb.europa.eu/")


def test_audit_known_truth():
    r = run_audit()
    assert r["n_observations"] == 500
    assert r["raw_level_sd_ratio_max_over_min"] == pytest.approx(187.5)
    assert r["rebased_max_spread_index_points"] < 1e-9
    assert r["vol_max_spread_across_series_pp"] < 1e-9
    assert r["vol_max_direct_vs_reciprocal_diff_pp"] < 1e-9


def test_all_five_figures_from_synthetic_sample(tmp_path):
    sample = write_sample(tmp_path / "sample.csv")
    out = tmp_path / "figs"
    paths = generate_all(sample, out)
    assert sorted(p.name for p in paths) == [
        "eur_usd_story.png", "eur_usd_volatility.png", "event_windows.png",
        "rebased_panel.png", "small_multiples.png"]
    assert all(p.exists() and p.stat().st_size > 5000 for p in paths)
