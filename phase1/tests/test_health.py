"""Phase 1: health entrypoint smoke tests."""

import pytest

from zomato_recommend import __version__
from zomato_recommend.cli import main


def test_main_prints_health(capsys) -> None:
    code = main([])
    out = capsys.readouterr().out
    assert code == 0
    assert __version__ in out
    assert "health: ok" in out
    assert "Phase 0" in out
    assert "Phase 1" in out
    assert "Phase 2" in out
    assert "Web UI" in out
    assert "Phase 3" in out
    assert "Phase 4" in out
    assert "Phase 5" in out
    assert "Phase 6" in out


def test_version_flag(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
