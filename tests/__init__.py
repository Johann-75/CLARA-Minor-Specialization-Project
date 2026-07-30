# CLARA Test Suite Package
import sys
import os

# Add parent directory to sys.path to enable smooth package resolutions during pytest invocations
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
