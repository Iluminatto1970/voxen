import json
import shutil
import re
from pathlib import Path


class SkillsCatalog:
    """
    Catalogo de skills inspirado em antigravity-awesome-skills.
    Permite listar e instalar skills do repositorio de referencia.
    """

    def __init__(
        self,
        source_root: str = "_references/antigravity-awesome-skills/skills",
        source_roots: list[str] | None = None,
        target_root: str = "skills",
        lock_file: str = "skills/skills.lock.json",
        health_file: str = "skills/skills.health.json",
    ) -> None:
        self.source_root = Path(source_root)
        merged_sources = source_roots or [
            ".agent/skills",
            "_references/antigravity-kit/.agent/skills",
            source_root,
        ]
        self.source_roots = [Path(item) for item in merged_sources]
        self.target_root = Path(target_root)
        self.target_root.mkdir(parents=True, exist_ok=True)
        self.lock_file = Path(lock_file)
        self.health_file = Path(health_file)
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.health_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.lock_file.exists():
            self._save_lock({"pins": {}})
        if not self.health_file.exists():
            self._save_health({"skills": {}})

    def _existing_source_roots(self) -> list[Path]:
        existing = []
        seen = set()
        for root in self.source_roots:
            resolved = str(root)
            if resolved in seen:
                continue
            seen.add(resolved)
            if root.exists() and root.is_dir():
                existing.append(root)
        return existing

    def _find_skill_source(self, skill_name: str) -> Path | None:
        for root in self._existing_source_roots():
            candidate = root / skill_name
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    def _load_lock(self) -> dict:
        try:
            return json.loads(self.lock_file.read_text(encoding="utf-8"))
        except Exception:
            return {"pins": {}}

    def _save_lock(self, payload: dict) -> None:
        self.lock_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_health(self) -> dict:
        try:
            return json.loads(self.health_file.read_text(encoding="utf-8"))
        except Exception:
            return {"skills": {}}

    def _save_health(self, payload: dict) -> None:
        self.health_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _touch_health(self, skill_name: str) -> dict:
        payload = self._load_health()
        skills = payload.setdefault("skills", {})
        skill = skills.setdefault(
            skill_name,
            {
                "installs": 0,
                "uninstalls": 0,
                "validations": 0,
                "issues": 0,
                "heal_runs": 0,
                "last_status": "unknown",
                "pinned_version": "latest",
            },
        )
        return skill

    def parse_skill_spec(self, skill_spec: str) -> tuple[str, str]:
        normalized = skill_spec.strip()
        if "@" not in normalized:
            return normalized, "latest"
        name, version = normalized.rsplit("@", 1)
        if not name:
            return normalized, "latest"
        return name.strip(), version.strip() or "latest"

    def get_pins(self) -> dict:
        return self._load_lock().get("pins", {})

    def pin_skill(self, skill_spec: str) -> tuple[bool, str]:
        name, version = self.parse_skill_spec(skill_spec)
        ok, msg = self.install(name)
        if not ok:
            return False, msg

        lock = self._load_lock()
        pins = lock.setdefault("pins", {})
        pins[name] = version
        self._save_lock(lock)

        health = self._load_health()
        skill = self._touch_health(name)
        skill["pinned_version"] = version
        health.setdefault("skills", {})[name] = skill
        self._save_health(health)

        return True, f"Skill '{name}' fixada na versao '{version}'."

    def unpin_skill(self, skill_name: str) -> tuple[bool, str]:
        name, _ = self.parse_skill_spec(skill_name)
        lock = self._load_lock()
        pins = lock.setdefault("pins", {})
        if name not in pins:
            return False, "Skill nao estava fixada."
        del pins[name]
        self._save_lock(lock)

        health = self._load_health()
        skill = self._touch_health(name)
        skill["pinned_version"] = "latest"
        health.setdefault("skills", {})[name] = skill
        self._save_health(health)

        return True, f"Skill '{name}' desfixada."

    def lock_status(self) -> dict:
        lock = self._load_lock()
        pins = lock.get("pins", {})
        return {
            "pins": pins,
            "count": len(pins),
            "lock_file": str(self.lock_file),
        }

    def enforce_pins(self) -> dict:
        lock = self._load_lock()
        pins = lock.get("pins", {})
        installed = set(self.list_installed())
        health = self._load_health().get("skills", {})

        issues = []
        for name, version in pins.items():
            if name not in installed:
                issues.append(f"{name}@{version}: skill pinada nao esta instalada")
                continue

            observed = health.get(name, {}).get("pinned_version", "latest")
            if observed != version:
                issues.append(
                    f"{name}@{version}: versao pinada diverge do estado ({observed})"
                )

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "pins": pins,
        }

    def sync_pins(self) -> dict:
        lock = self._load_lock()
        pins = lock.get("pins", {})
        repaired = []
        failed = []

        for name, version in pins.items():
            ok, _ = self.install(name)
            if not ok:
                failed.append(name)
                continue

            health_payload = self._load_health()
            skill = self._touch_health(name)
            skill["pinned_version"] = version
            skill["last_status"] = "pin_synced"
            health_payload.setdefault("skills", {})[name] = skill
            self._save_health(health_payload)
            repaired.append(name)

        status = "ok" if not failed else "partial"
        return {
            "status": status,
            "repaired": repaired,
            "failed": failed,
            "pins": pins,
        }

    def list_available(self, limit: int = 100) -> list[str]:
        names: set[str] = set()
        for root in self._existing_source_roots():
            for skill_dir in root.iterdir():
                if skill_dir.is_dir():
                    names.add(skill_dir.name)
        skills = sorted(names)
        skills.sort()
        return skills[:limit]

    def _skill_metadata(self, skill_dir: Path) -> dict:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return {
                "name": skill_dir.name,
                "has_skill_md": False,
                "title": "",
                "tags": [],
            }

        try:
            content = skill_file.read_text(encoding="utf-8")
        except Exception:
            content = ""

        title = ""
        tags: list[str] = []
        for line in content.splitlines()[:40]:
            stripped = line.strip()
            if stripped.startswith("# ") and not title:
                title = stripped[2:].strip()
            if stripped.lower().startswith("tags:"):
                raw = stripped.split(":", 1)[1]
                tags = [t.strip() for t in raw.split(",") if t.strip()]

        return {
            "name": skill_dir.name,
            "has_skill_md": True,
            "title": title,
            "tags": tags,
        }

    def list_available_with_metadata(self, limit: int = 100) -> list[dict]:
        all_names = self.list_available(limit=2000)
        metadata = []
        for name in all_names:
            source = self._find_skill_source(name)
            if source is not None:
                metadata.append(self._skill_metadata(source))
        return metadata[:limit]

    def list_installed(self) -> list[str]:
        installed = [p.name for p in self.target_root.iterdir() if p.is_dir()]
        installed.sort()
        return installed

    def translate_skill_name(self, skill_name: str) -> str:
        token_map = {
            "api": "api",
            "apis": "apis",
            "agent": "agente",
            "agents": "agentes",
            "ai": "ia",
            "automation": "automacao",
            "backend": "backend",
            "build": "build",
            "builder": "construtor",
            "bug": "bug",
            "bugs": "bugs",
            "chat": "chat",
            "checkout": "checkout",
            "clean": "limpo",
            "cli": "linha de comando",
            "code": "codigo",
            "coverage": "cobertura",
            "data": "dados",
            "database": "banco de dados",
            "debug": "depuracao",
            "deploy": "deploy",
            "design": "design",
            "developer": "desenvolvedor",
            "development": "desenvolvimento",
            "docs": "documentacao",
            "documentation": "documentacao",
            "endpoint": "endpoint",
            "frontend": "frontend",
            "fullstack": "fullstack",
            "generator": "gerador",
            "integration": "integracao",
            "landing": "landing page",
            "lint": "lint",
            "mobile": "mobile",
            "nextjs": "nextjs",
            "performance": "performance",
            "python": "python",
            "qa": "qa",
            "rag": "rag",
            "react": "react",
            "review": "revisao",
            "rust": "rust",
            "security": "seguranca",
            "seo": "seo",
            "skill": "skill",
            "skills": "skills",
            "stripe": "stripe",
            "test": "teste",
            "testing": "testes",
            "tool": "ferramenta",
            "tools": "ferramentas",
            "ui": "ui",
            "ux": "ux",
            "vector": "vetor",
            "workflow": "fluxo",
            "workflows": "fluxos",
        }

        tokens = re.split(r"[-_\s]+", skill_name.lower())
        translated = [token_map.get(token, token) for token in tokens if token]
        return " ".join(translated).strip()

    def format_skill_label(self, skill_name: str) -> str:
        translated = self.translate_skill_name(skill_name)
        if translated and translated != skill_name:
            return f"{skill_name} ({translated})"
        return skill_name

    def format_skill_labels(self, skill_names: list[str]) -> list[str]:
        return [self.format_skill_label(name) for name in skill_names]

    def install(self, skill_name: str) -> tuple[bool, str]:
        name, _ = self.parse_skill_spec(skill_name)
        source = self._find_skill_source(name)
        if source is None:
            return False, "Skill nao encontrada no catalogo de referencia."

        target = self.target_root / name
        if target.exists():
            health_payload = self._load_health()
            health = self._touch_health(name)
            health["last_status"] = "already_installed"
            health_payload.setdefault("skills", {})[name] = health
            self._save_health(health_payload)
            return True, "Skill ja instalada."

        try:
            shutil.copytree(source, target)
        except FileExistsError:
            return True, "Skill ja instalada."

        health_payload = self._load_health()
        health = self._touch_health(name)
        health["installs"] += 1
        health["last_status"] = "installed"
        health_payload.setdefault("skills", {})[name] = health
        self._save_health(health_payload)

        pins = self._load_lock().get("pins", {})
        if name in pins:
            return True, f"Skill '{name}' instalada (pin {pins[name]})."
        return True, f"Skill '{name}' instalada em {target}."

    def uninstall(self, skill_name: str) -> tuple[bool, str]:
        name, _ = self.parse_skill_spec(skill_name)
        target = self.target_root / name
        if not target.exists():
            return False, "Skill nao instalada."
        shutil.rmtree(target)

        health_payload = self._load_health()
        health = self._touch_health(name)
        health["uninstalls"] += 1
        health["last_status"] = "uninstalled"
        health_payload.setdefault("skills", {})[name] = health
        self._save_health(health_payload)

        return True, f"Skill '{name}' removida."

    def validate_installed(self) -> dict:
        issues = []
        for skill_dir in [p for p in self.target_root.iterdir() if p.is_dir()]:
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                issues.append(f"{skill_dir.name}: SKILL.md ausente")
                continue

            try:
                content = skill_file.read_text(encoding="utf-8")
            except Exception as exc:
                issues.append(f"{skill_dir.name}: falha de leitura ({exc})")
                continue

            if not re.search(r"^#\s+", content, flags=re.MULTILINE):
                issues.append(f"{skill_dir.name}: sem titulo principal")
            if "TODO" in content:
                issues.append(f"{skill_dir.name}: contem TODO pendente")

        health_payload = self._load_health()
        for skill_name in self.list_installed():
            health = self._touch_health(skill_name)
            health["validations"] += 1
            health_payload.setdefault("skills", {})[skill_name] = health

        for issue in issues:
            prefix = issue.split(":", 1)[0].strip()
            health = self._touch_health(prefix)
            health["issues"] += 1
            health["last_status"] = "issue"
            health_payload.setdefault("skills", {})[prefix] = health

        self._save_health(health_payload)

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "checked": len([p for p in self.target_root.iterdir() if p.is_dir()]),
        }

    def health_summary(self) -> dict:
        payload = self._load_health()
        skills = payload.get("skills", {})
        summary = []
        for name, metrics in skills.items():
            installs = metrics.get("installs", 0)
            validations = metrics.get("validations", 0)
            issues = metrics.get("issues", 0)
            heals = metrics.get("heal_runs", 0)
            score = max(0.0, min(100.0, 70 + installs * 1.5 + validations * 0.5 - issues * 8 + heals * 2))
            summary.append(
                {
                    "name": name,
                    "score": round(score, 2),
                    "installs": installs,
                    "validations": validations,
                    "issues": issues,
                    "heal_runs": heals,
                    "last_status": metrics.get("last_status", "unknown"),
                    "pinned_version": metrics.get("pinned_version", "latest"),
                }
            )
        summary.sort(key=lambda item: item["score"], reverse=True)
        avg = round(sum(item["score"] for item in summary) / len(summary), 2) if summary else 0.0
        return {"skills": summary, "average": avg, "count": len(summary)}

    def heal_skills(self) -> dict:
        report = self.validate_installed()
        problematic = set()
        for issue in report.get("issues", []):
            name = issue.split(":", 1)[0].strip()
            if name:
                problematic.add(name)

        healed = []
        failed = []
        for name in sorted(problematic):
            self.uninstall(name)
            ok, _ = self.install(name)
            health_payload = self._load_health()
            health = self._touch_health(name)
            health["heal_runs"] += 1
            health["last_status"] = "healed" if ok else "heal_failed"
            health_payload.setdefault("skills", {})[name] = health
            self._save_health(health_payload)

            if ok:
                healed.append(name)
            else:
                failed.append(name)

        return {
            "detected_issues": len(problematic),
            "healed": healed,
            "failed": failed,
            "status": "ok" if not failed else "partial",
        }

    def recommend(self, mode_name: str, intent: str = "", limit: int = 8) -> list[str]:
        available = self.list_available(limit=2000)
        if not available:
            return []

        mode_token_weights = {
            "micro_saas": {
                "next": 4,
                "stripe": 5,
                "api": 3,
                "frontend": 4,
                "seo": 3,
                "tailwind": 4,
                "react": 4,
                "checkout": 5,
                "conversion": 4,
                "landing": 4,
            },
            "dev_tool_cli": {
                "python": 5,
                "rust": 5,
                "cli": 6,
                "debug": 4,
                "testing": 4,
                "lint": 4,
                "security": 4,
                "terminal": 5,
                "performance": 4,
            },
            "support_agent": {
                "rag": 6,
                "api": 4,
                "automation": 4,
                "workflow": 4,
                "integration": 5,
                "chat": 5,
                "whatsapp": 5,
                "vector": 5,
                "knowledge": 4,
            },
        }

        weights = mode_token_weights.get(mode_name, {})
        tokens = [t.lower() for t in weights.keys()]
        if intent:
            tokens.extend(re.findall(r"[a-zA-Z0-9_-]+", intent.lower()))

        scored = []
        for name in available:
            score = 0
            lower = name.lower()
            for token in tokens:
                if token and token in lower:
                    score += weights.get(token, 1)
            if score > 0:
                scored.append((score, name))

        if not scored:
            fallback = [
                name
                for name in available
                if any(x in name.lower() for x in ["debug", "testing", "api", "clean", "architecture"])
            ]
            return fallback[:limit]

        scored.sort(key=lambda item: item[0], reverse=True)
        return [name for _, name in scored[:limit]]
