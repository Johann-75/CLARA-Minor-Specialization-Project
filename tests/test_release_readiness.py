"""Release and deployment readiness checks for the submission repository."""

from pathlib import Path
import configparser
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


def test_coverage_configuration_targets_runtime_application_packages():
    config_path = ROOT / ".coveragerc"
    parser = configparser.ConfigParser()
    assert parser.read(config_path, encoding="utf-8") == [str(config_path)]

    sources = {line.strip() for line in parser["run"]["source"].splitlines() if line.strip()}
    omit = {line.strip() for line in parser["run"]["omit"].splitlines() if line.strip()}

    assert sources == {"analytics", "dashboard", "data_generator", "genai", "warehouse"}
    assert "tests/*" in omit
    assert "docs/*" in omit
    assert ".python311/*" in omit


def test_evaluator_markdown_matches_verified_submission_metrics():
    documents = [
        ROOT / "README.md",
        ROOT / "docs" / "final" / "PROJECT_OVERVIEW.md",
        ROOT / "docs" / "final" / "DEMO_GUIDE.md",
        ROOT / "docs" / "final" / "INSTALLATION_GUIDE.md",
        ROOT / "docs" / "final" / "VIVA_QUESTIONS_AND_ANSWERS.md",
        ROOT / "docs" / "final" / "CLARA_Presentation_Script.md",
        ROOT / "docs" / "final" / "screenshots" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in documents)

    banned = [
        r"c:\Users\Nandan Murali",
        "python -m warehouse.db",
        "100 AWS EC2, 100 Azure VM, 100 GCP Compute Engine",
        "$220.87 in actionable monthly cost waste",
        "$220.87 actionable monthly waste",
        "Actionable Cost Waste: $220.87",
        "75 Passing Tests, 80% Statement Coverage",
        "80% total statement coverage",
        "80% Total Statement Coverage",
        "Date: [Day Month Year]",
    ]
    for stale_claim in banned:
        assert stale_claim not in combined

    required = [
        "AWS 155 / Azure 88 / GCP 57",
        "15 injected",
        "17 predicted",
        "$184.58",
        "$220.87",
        "67%",
        "November 3, 2026",
    ]
    for verified_claim in required:
        assert verified_claim in combined

