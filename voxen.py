import argparse
import os
from pathlib import Path

from voxen_cli import main, run_interactive_command, run_single_command


INTERACTIVE_COMMAND_PREFIX = "__VOXEN_INTERACTIVE_COMMAND__::"


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


def _normalize_direct_input(tokens: list[str], raw: str = "") -> str:
    text = (raw or "").strip()
    if text:
        lowered = text.lower()
        interactive_aliases = {
            "/voxen-plan": "/voxen plan",
            "voxen-plan": "/voxen plan",
            "/voxen-brainstorm": "/voxen brainstorm",
            "voxen-brainstorm": "/voxen brainstorm",
            "/voxen-create": "/voxen create",
            "voxen-create": "/voxen create",
            "/voxen-debug": "/voxen debug",
            "voxen-debug": "/voxen debug",
            "/voxen-enhance": "/voxen enhance",
            "voxen-enhance": "/voxen enhance",
            "/voxen-preview": "/voxen preview",
            "voxen-preview": "/voxen preview",
            "/voxen-orchestrate": "/voxen orchestrate",
            "voxen-orchestrate": "/voxen orchestrate",
            "/voxen-test": "/voxen test",
            "voxen-test": "/voxen test",
            "/voxen-deploy": "/voxen deploy",
            "voxen-deploy": "/voxen deploy",
            "/voxen-status": "/voxen status",
            "voxen-status": "/voxen status",
            "/voxen-ui-ux-pro-max": "/voxen ui-ux-pro-max",
            "voxen-ui-ux-pro-max": "/voxen ui-ux-pro-max",
            "/voxen-discovery-to-delivery": "/voxen discovery-to-delivery",
            "voxen-discovery-to-delivery": "/voxen discovery-to-delivery",
        }
        if lowered in interactive_aliases:
            target = interactive_aliases[lowered]
            return f"{INTERACTIVE_COMMAND_PREFIX}{target}"
        for alias, target in interactive_aliases.items():
            prefix = f"{alias} "
            if lowered.startswith(prefix):
                suffix = text[len(prefix):].strip()
                full_target = f"{target} {suffix}".strip()
                return f"{INTERACTIVE_COMMAND_PREFIX}{full_target}"
        if text.startswith("/voxen ") or text == "/voxen":
            return text
        if text.startswith("/"):
            return f"/voxen {text[1:]}"
        parts = text.split(None, 1)
        if parts and parts[0].lower() in {
            "plan",
            "brainstorm",
            "create",
            "debug",
            "enhance",
            "preview",
            "orchestrate",
            "test",
            "deploy",
            "ui-ux-pro-max",
            "discovery-to-delivery",
            "workflow",
            "status",
            "skills",
            "list",
            "context",
            "route",
            "workflows",
            "specialists",
            "bundle",
            "eval",
            "profiles",
        }:
            return f"/voxen {text}"
        return text

    joined = " ".join(tokens).strip()
    if not joined:
        return ""
    return _normalize_direct_input([], joined)


if __name__ == "__main__":
    _bootstrap_env()
    parser = argparse.ArgumentParser(description="Voxen CLI")
    parser.add_argument(
        "--cmd",
        help="Executa comando direto; encadeie com ';;' (ex: '/voxen context;;/voxen status')",
        default="",
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="Atalho: voxen plan <texto> | voxen brainstorm <texto> | voxen /voxen <comando>",
    )
    args = parser.parse_args()
    direct_cmd = _normalize_direct_input(args.command, args.cmd)
    if direct_cmd.startswith(INTERACTIVE_COMMAND_PREFIX):
        command = direct_cmd.replace(INTERACTIVE_COMMAND_PREFIX, "", 1)
        raise SystemExit(run_interactive_command(command))
    if direct_cmd:
        raise SystemExit(run_single_command(direct_cmd))
    main()
