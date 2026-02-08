"""Lightweight deployment validation for zerodha_bot."""

from pathlib import Path

try:
    from .config import missing_env_vars
except ImportError:  # script execution fallback
    from config import missing_env_vars

BASE_DIR = Path(__file__).resolve().parent


def main():
    required = ["KITE_API_KEY", "KITE_ACCESS_TOKEN", "TELEGRAM_TOKEN"]
    missing = missing_env_vars(*required)

    print("Deployment check:")
    print(f"- Base directory: {BASE_DIR}")
    print(f"- Logs dir exists: {(BASE_DIR / 'logs').exists()}")
    print(f"- Predictions file exists: {(BASE_DIR / 'predictions.json').exists()}")

    if missing:
        print(f"- Missing required env vars: {', '.join(missing)}")
        return 1

    print("- Env validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
