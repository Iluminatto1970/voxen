import subprocess
import re
from pathlib import Path


class QASkill:
    """
    Skill de Testes: o filtro de qualidade do Iluminatto.
    """

    def __init__(self, workspace_dir: str = "workspace") -> None:
        self.workspace = Path(workspace_dir)

    def run_security_check(self, file_path: str) -> tuple[bool, str]:
        target = self.workspace / file_path
        if not target.exists():
            return False, f"Arquivo não encontrado para análise: {file_path}"

        content = target.read_text(encoding="utf-8")
        lowered = content.lower()
        risky_tokens = ["api_key", "password", "secret", "token="]

        for token in risky_tokens:
            if token in lowered:
                return False, f"VULNERABILIDADE: possível credencial exposta ({token})."

        return True, "Segurança básica OK."

    def run_unit_tests(self, test_command: str) -> tuple[bool, str]:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.workspace,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            return False, f"TESTE FALHOU: {stderr}"
        return True, "Testes aprovados. Código estável."

    def run_unit_tests_verbose(self, test_command: str) -> tuple[bool, str, str]:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.workspace,
        )
        combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
        if result.returncode != 0:
            msg = (result.stderr.strip() or result.stdout.strip() or "Teste falhou sem saida")
            return False, f"TESTE FALHOU: {msg}", combined_output
        return True, "Testes aprovados. Código estável.", combined_output

    def check_coverage_threshold(
        self,
        report_text: str,
        minimum_percent: float = 80.0,
    ) -> tuple[bool, str]:
        patterns = [
            r"TOTAL\s+\d+\s+\d+\s+(\d+)%",
            r"coverage[:\s]+(\d+(?:\.\d+)?)%",
            r"all files\s*\|[^\n]*\|(\s*\d+(?:\.\d+)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, report_text, flags=re.IGNORECASE)
            if not match:
                continue
            value = float(match.group(1))
            if value >= minimum_percent:
                return True, f"Cobertura OK: {value:.1f}% >= {minimum_percent:.1f}%"
            return False, f"Cobertura abaixo do limite: {value:.1f}% < {minimum_percent:.1f}%"

        return False, "Nao foi possivel identificar percentual de cobertura no relatorio."


qa = QASkill()
