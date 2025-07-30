#!/usr/bin/env python3
"""
Test script to demonstrate the new export formats functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parser import EnvyroParser


def test_export_formats():
    """Test exporting to different formats."""
    config_file = Path(__file__).parent / "config.envyro"

    if not config_file.exists():
        print(f"Config file not found: {config_file}")
        return

    parser = EnvyroParser(str(config_file))

    formats = ["env", "json", "yaml", "toml"]
    environments = ["dev", "prod"]

    for env in environments:
        print(f"\n=== Testing environment: {env} ===")

        for fmt in formats:
            try:
                output_file = f"test_output_{env}.{fmt}"
                parser.export_format(env, fmt, output_file)  # type: ignore
                print(f"✅ Successfully exported to {fmt}: {output_file}")

                if Path(output_file).exists():
                    with open(output_file, "r") as f:
                        content = f.read()
                        print(f"   Preview: {content[:100]}...")

            except Exception as e:
                print(f"❌ Failed to export to {fmt}: {e}")


if __name__ == "__main__":
    test_export_formats()
