"""
Quick command-line test of the full pipeline, without needing FastAPI running.

Usage:
    cd backend
    python run_cli.py "A subscription box that sends regional Indian spice
    blends with recipe cards, targeted at the Indian diaspora abroad."
"""
import json
import sys

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from backend.orchestrator import analyze_startup


def main():
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = input("Describe the startup idea: ").strip()

    print(f"\nAnalyzing: {idea}\n{'=' * 60}\n")
    result = analyze_startup(idea)

    for section in ["market_report", "competitor_report", "customer_report",
                     "business_report", "risk_report"]:
        title = section.replace("_", " ").title()
        print(f"\n--- {title} ---\n{result[section]}\n")

    print(f"\n--- Final Synthesis ---\n{json.dumps(result['synthesis'], indent=2)}\n")
    print(f"(Completed in {result['elapsed_seconds']}s)")


if __name__ == "__main__":
    main()
