import subprocess
import time
import json
import sys
import os

def run_command(command, description):
    print(f"\n[+] {description}")
    print(f"    Running: {command}")
    start = time.time()
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        elapsed = time.time() - start
        print(f"    Completed in {elapsed:.2f}s")
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"    [!] Failed in {elapsed:.2f}s")
        print(f"    Output: {e.stdout}")
        print(f"    Error: {e.stderr}")
        sys.exit(1)

def main():
    print("=== STARTING BENCHMARK: OPERATION SCALE-ORCHESTRATOR ===")

    # Part 1
    stdout, _ = run_command("python src/main.py map .", "Part 1: The Cold Scan (Mapping Efficiency)")
    print("    Output:", stdout.strip())

    # Part 2
    stdout, _ = run_command("python src/main.py analyze . --focus security", "Part 2: The Deep Reasoning (Multi-Agent Logic)")
    print("    Output excerpt:", stdout.strip()[:200] + "...")

    # Part 3
    stdout, _ = run_command("python src/main.py costs --timerange today --format json", "Part 3: Cost & Performance Audit")
    print("    Output:", stdout.strip())

    # Part 4
    stdout, _ = run_command("python src/main.py report --type performance --format html", "Part 4: Report Generation")
    print("    Output:", stdout.strip())

    print("\n=== BENCHMARK COMPLETE ===")

if __name__ == "__main__":
    main()
