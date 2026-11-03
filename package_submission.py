"""
Script to create the clean CLARA Final Submission ZIP package.
Excludes virtual environments, environment files (.env), caches, and temporary files.
Performs an automated secret scan on all packaged files.
"""

import os
import zipfile
import hashlib
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUT = os.path.join(ROOT_DIR, "CLARA_Final_Submission.zip")

EXCLUDE_DIRS = {
    ".venv", "venv", "__pycache__", ".pytest_cache", ".git", ".github",
    "scratch", ".idea", ".vscode"
}

EXCLUDE_FILES = {
    ".env", "CLARA_Final_Submission.zip", ".coverage", "clara.db.tmp"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd"
}

SECRET_PATTERNS = [
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),  # Google API key pattern
    re.compile(r"AKIA[0-9A-Z]{16}"),         # AWS Access Key pattern
    re.compile(r"ghp_[A-Za-z0-9]{36}"),      # GitHub Personal Access Token
]


def create_clean_zip():
    print(f"Creating clean submission package: {ZIP_OUT}")
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)

    packaged_files = 0
    total_size = 0
    secret_hits = []

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith(".egg-info")]

            rel_dir = os.path.relpath(root, ROOT_DIR)
            if any(part in EXCLUDE_DIRS for part in rel_dir.split(os.sep)):
                continue

            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                if file.startswith(".env") and file != ".env.example":
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, ROOT_DIR)

                # Secret Scan (for text files)
                if not any(file.endswith(ext) for ext in [".db", ".png", ".jpg", ".docx", ".pdf", ".pptx", ".doc"]):
                    try:
                        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for pat in SECRET_PATTERNS:
                                matches = pat.findall(content)
                                if matches:
                                    secret_hits.append((rel_path, matches))
                    except Exception:
                        pass

                zf.write(abs_path, rel_path)
                packaged_files += 1
                total_size += os.path.getsize(abs_path)

    # Compute SHA256 of ZIP
    h = hashlib.sha256()
    with open(ZIP_OUT, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    zip_hash = h.hexdigest()
    zip_size_mb = os.path.getsize(ZIP_OUT) / (1024 * 1024)

    print("\n============================================================")
    print("CLARA FINAL SUBMISSION PACKAGE AUDIT")
    print("============================================================")
    print(f"Archive Path   : {ZIP_OUT}")
    print(f"Packaged Files : {packaged_files}")
    print(f"Archive Size   : {zip_size_mb:.2f} MB")
    print(f"Archive SHA256 : {zip_hash}")
    print(f"Secret Scan    : {'PASSED (0 secrets detected)' if not secret_hits else f'FAILED ({len(secret_hits)} hits)'}")
    if secret_hits:
        for spath, smatches in secret_hits:
            print(f"  WARNING: Potential secret in {spath}: {smatches}")
    print("============================================================\n")


if __name__ == "__main__":
    create_clean_zip()
