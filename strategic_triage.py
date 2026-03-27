import json
from pathlib import Path


class StrategicTriage:
    """
    Filtro de guerra: define o destino do Squad por ROI e esforco.
    Tambem trava o modo ate o primeiro deploy ser concluido.
    """

    def __init__(self, lock_file: str = "voxen_mission_lock.json") -> None:
        self.lock_file = Path(lock_file)

    def _ask_yes_no(self, prompt: str) -> bool:
        while True:
            answer = input(f"{prompt} (s/n): ").strip().lower()
            if answer in {"s", "sim", "y", "yes"}:
                return True
            if answer in {"n", "nao", "não", "no"}:
                return False
            print("Resposta invalida. Use 's' ou 'n'.")

    def load_lock(self) -> dict | None:
        if not self.lock_file.exists():
            return None
        try:
            return json.loads(self.lock_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def save_lock(self, mode: str, instruction: str) -> None:
        payload = {
            "mode": mode,
            "instruction": instruction,
            "first_deploy_completed": False,
        }
        self.lock_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def set_first_deploy_completed(self) -> bool:
        data = self.load_lock()
        if not data:
            return False
        data["first_deploy_completed"] = True
        self.lock_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True

    def ask_strategy(self) -> tuple[str, str]:
        print("--- DIAGNOSTICO ESTRATEGICO OPENCODE ---")
        q1 = self._ask_yes_no("1. O objetivo e receita recorrente imediata?")
        q2 = self._ask_yes_no("2. O foco e performance bruta e uso tecnico/terminal?")
        q3 = self._ask_yes_no(
            "3. Precisa integrar com canais de chat e bases de conhecimento?"
        )

        if q1:
            return "MICRO_SAAS", "Foco em Stripe, Auth e UI de conversao."
        if q2:
            return "DEV_TOOL_CLI", "Foco em Rust/Python, latencia zero e seguranca."
        if q3:
            return "SUPPORT_AGENT", "Foco em RAG, VectorDB e APIs de mensageria."
        return "MVP_GENERIC", "Foco em validacao rapida de ideia."


triage = StrategicTriage()
