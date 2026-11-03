"""Release and deployment readiness checks for the submission repository."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def _ignored_paths(relative_paths: list[str]) -> set[str]:
    result = subprocess.run(
        ["git", "check-ignore", "--stdin", "-z"],
        cwd=ROOT,
        input="\0".join(relative_paths) + "\0",
        text=True,
        capture_output=True,
        check=False,
    )
    return {path for path in result.stdout.split("\0") if path}


def test_release_ignore_policy_protects_local_artifacts_and_includes_active_database():
    forbidden = [
        ".env",
        "clara.db.live_backup",
        ".venv/pyvenv.cfg",
        ".python311/python.exe",
        ".python311-embed.zip",
        ".tmp_pip/download.tmp",
        ".coverage",
        ".pytest_cache/README.md",
        "streamlit.stdout.log",
        "streamlit.stderr.log",
        ".superpowers/sdd/progress.md",
    ]

    checked = forbidden + ["clara.db"]
    ignored = _ignored_paths(checked)

    assert set(forbidden) <= ignored
    assert "clara.db" not in ignored


def test_streamlit_deployment_files_exist_without_embedded_secrets():
    python_version = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")

    assert python_version == "3.11"
    assert "headless = true" in config
    assert "GEMINI_API_KEY" not in config

