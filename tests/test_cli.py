from __future__ import annotations

import mnemos.cli as cli


def test_main_runs_bot(monkeypatch) -> None:
    called = False

    async def fake_run() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "run", fake_run)

    cli.main([])

    assert called
