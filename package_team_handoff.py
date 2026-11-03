"""
Package CLARA Team Handoff Archive (CLARA_Team_Handoff.zip).

Includes:
- Complete project source code (analytics, dashboard, data_generator, genai, warehouse)
- Interactive Streamlit dashboard
- Analytical models and trained weights
- Synthetic data generator and dataset (including held-out anomaly_manifest.json)
- Test suite (75 tests)
- Documentation generators and university reference material
- Configuration files, requirements files, .env.example
- Production DuckDB database (clara.db and clara.db.live_backup)

Excludes:
- .env
- Every API key or credential
- .venv/
- venv/
- test_env/
- __pycache__/
- *.pyc, *.pyo, *.pyd
- .pytest_cache/
- coverage files (.coverage, .coverage.*, htmlcov/)
- scratch/
- temporary logs (*.log, *.tmp, *.bak)
- existing ZIP files (*.zip)
- .git/

Runs an automated secret scan over every text/code file included in the archive.
"""

import os
import zipfile
import hashlib
import re
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUT = os.path.join(ROOT_DIR, "CLARA_Team_Handoff.zip")

EXCLUDE_DIR_NAMES = {
    ".venv", "venv", "test_env", "__pycache__", ".pytest_cache",
    ".git", "scratch", ".idea", ".vscode", "htmlcov"
}

EXCLUDE_FILE_NAMES = {
    ".env", ".coverage", "clara.db.tmp"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".log", ".tmp", ".bak", ".zip", ".lock"
}

SECRET_PATTERNS = [
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),               # Google API key pattern
    re.compile(r"AKIA[0-9A-Z]{16}"),                      # AWS Access Key pattern
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                   # GitHub Personal Access Token
    re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),         # Slack token
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----") # Private keys
]

def is_excluded_path(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    # Check directory components
    for part in parts[:-1]:
        if part in EXCLUDE_DIR_NAMES:
            return True
        if part.endswith(".egg-info"):
            return True

    filename = parts[-1]
    # Check temporary lock files (e.g. MS Office ~$...)
    if filename.startswith("~$") or filename.startswith(".~"):
        return True
    # Check filename exclusions
    if filename in EXCLUDE_FILE_NAMES:
        return True
    # Exclude any .env file that isn't .env.example
    if filename.startswith(".env") and filename != ".env.example":
        return True
    # Exclude coverage files
    if filename.startswith(".coverage"):
        return True
    # Check extension exclusions
    for ext in EXCLUDE_EXTS:
        if filename.lower().endswith(ext):
            return True

    return False


def build_team_handoff():
    print(f"Building Team Handoff Archive: {ZIP_OUT}")
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)

    files_to_pack = []

    for root, dirs, files in os.walk(ROOT_DIR):
        # Prune dirs in place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES and not d.endswith(".egg-info")]

        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, ROOT_DIR)
            if is_excluded_path(rel_path):
                continue
            files_to_pack.append((abs_path, rel_path))

    # Sort files deterministically
    files_to_pack.sort(key=lambda x: x[1])

    secret_hits = []
    binary_exts = {".db", ".png", ".jpg", ".docx", ".pdf", ".pptx", ".doc", ".pkl"}

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for abs_path, rel_path in files_to_pack:
            # Secret scan on text/source files
            filename = os.path.basename(abs_path)
            _, ext = os.path.splitext(filename)
            if ext.lower() not in binary_exts:
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                        for pat in SECRET_PATTERNS:
                            matches = pat.findall(content)
                            if matches:
                                secret_hits.append((rel_path, matches))
                except Exception as e:
                    print(f"Warning: could not scan {rel_path}: {e}")

            zf.write(abs_path, rel_path)

    # Re-verify archive by reading it back
    print("Verifying archive integrity and contents...")
    archive_file_count = 0
    total_uncompressed_bytes = 0
    forbidden_entries = []
    pyarrow_verified = False

    with zipfile.ZipFile(ZIP_OUT, "r") as zf:
        infolist = zf.infolist()
        archive_file_count = len(infolist)
        for info in infolist:
            name = info.filename
            total_uncompressed_bytes += info.file_size
            if is_excluded_path(name):
                forbidden_entries.append(name)

            if name == "requirements.txt":
                req_text = zf.read(name).decode("utf-8")
                if "pyarrow==16.1.0" in req_text:
                    pyarrow_verified = True
                else:
                    print("ERROR: pyarrow==16.1.0 NOT found in requirements.txt!")

            # Scan text files from within zip
            _, ext = os.path.splitext(name)
            if ext.lower() not in binary_exts:
                try:
                    file_bytes = zf.read(name)
                    text = file_bytes.decode("utf-8", errors="ignore")
                    for pat in SECRET_PATTERNS:
                        m = pat.findall(text)
                        if m and (name, m) not in secret_hits:
                            secret_hits.append((name, m))
                except Exception as e:
                    print(f"Warning: could not scan zip entry {name}: {e}")

    # Compute SHA256 of the ZIP file
    sha256 = hashlib.sha256()
    with open(ZIP_OUT, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    zip_sha256 = sha256.hexdigest().upper()
    zip_size_bytes = os.path.getsize(ZIP_OUT)
    zip_size_mb = zip_size_bytes / (1024 * 1024)

    print("\n" + "=" * 60)
    print("CLARA TEAM HANDOFF ARCHIVE AUDIT REPORT")
    print("=" * 60)
    print(f"1. ZIP Location   : {ZIP_OUT}")
    print(f"2. File Count     : {archive_file_count}")
    print(f"3. Size           : {zip_size_bytes:,} bytes ({zip_size_mb:.2f} MB)")
    print(f"   (Uncompressed) : {total_uncompressed_bytes:,} bytes ({total_uncompressed_bytes / (1024*1024):.2f} MB)")
    print(f"4. SHA256 Hash    : {zip_sha256}")
    print(f"5. pyarrow Pin    : {'VERIFIED (pyarrow==16.1.0)' if pyarrow_verified else 'FAILED'}")
    print(f"6. Forbidden Items: {'NONE (0 forbidden files)' if not forbidden_entries else f'FAILED: {forbidden_entries}'}")
    print(f"7. Secret Scan    : {'PASSED (0 secrets detected)' if not secret_hits else f'FAILED ({len(secret_hits)} secrets detected)'}")
    print("=" * 60 + "\n")

    if forbidden_entries or secret_hits or not pyarrow_verified:
        print("Archive validation FAILED!")
        sys.exit(1)

    return {
        "location": ZIP_OUT,
        "count": archive_file_count,
        "size_bytes": zip_size_bytes,
        "size_mb": zip_size_mb,
        "sha256": zip_sha256,
        "secret_hits": secret_hits,
        "forbidden_entries": forbidden_entries,
        "pyarrow_verified": pyarrow_verified
    }

if __name__ == "__main__":
    build_team_handoff()
