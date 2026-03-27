import argparse
import os
from pathlib import Path

from voxen_cli import main, run_single_command


def _load_env_file(file_path: Path) -> None:
    if not file_path.exists():
        return
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


def _bootstrap_env() -> None:
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / ".env",
        script_dir / ".env.local",
        cwd / ".env",
        cwd / ".env.local",
    ]
    for candidate in candidates:
        _load_env_file(candidate)


if __name__ == "__main__":
    _bootstrap_env()
    parser = argparse.ArgumentParser(description="Voxen CLI")
    parser.add_argument(
        "--cmd",
        help="Executa comando direto; encadeie com ';;' (ex: '/voxen context;;/voxen status')",
        default="",
    )
    args = parser.parse_args()
    if args.cmd:
        raise SystemExit(run_single_command(args.cmd))
    main()
