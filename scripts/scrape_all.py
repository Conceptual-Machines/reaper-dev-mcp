#!/usr/bin/env python3
"""
Run all scrapers/parsers to update API data.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

SCRIPTERS = [
    ("JSFX", "scrape_jsfx.py"),
    ("ReaScript", "scrape_reascript.py"),
    ("ReaWrap", "parse_reawrap.py"),
]

def main():
    """Run all scrapers."""
    print("=== Running all API scrapers/parsers ===\n")
    
    for name, script in SCRIPTERS:
        print(f"\n--- Running {name} scraper ---")
        script_path = SCRIPTS_DIR / script
        try:
            result = subprocess.run(
                ["python3.13", str(script_path)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            if result.returncode != 0:
                print(f"Error: {name} scraper failed with code {result.returncode}", file=sys.stderr)
        except Exception as e:
            print(f"Error running {name} scraper: {e}", file=sys.stderr)
    
    print("\n=== All scrapers completed ===")

if __name__ == "__main__":
    main()

