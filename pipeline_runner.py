from memory_hub import MemoryHub
from message_bus import MessageBus
from concurrent.futures import ThreadPoolExecutor
from voxen_bridge import VoxenBridge
from voxen_manager import AgentRole


class PipelineRunner:
    """
    Runner de pipeline com checkpoints e memoria persistente.
    """

    def __init__(
        self,
        bridge: VoxenBridge,
        message_bus: MessageBus,
        memory_hub: MemoryHub,
    ) -> None:
        self.bridge = bridge
        self.bus = message_bus
        self.memory = memory_hub

    def _parse_role(self, role_label: str) -> AgentRole:
        normalized = role_label.strip().lower()
        role_map = {
            "manager": AgentRole.MANAGER,
            "dev": AgentRole.DEVELOPER,
            "developer": AgentRole.DEVELOPER,
            "tester": AgentRole.QA,
            "qa": AgentRole.QA,
            "growth": AgentRole.GROWTH,
        }
        return role_map.get(normalized, AgentRole.DEVELOPER)

    def run(self, pipeline_name: str, steps: list[dict]) -> dict:
        self.memory.remember(
            kind="pipeline_start",
            content=f"Pipeline {pipeline_name} iniciada com {len(steps)} etapas.",
            metadata={"pipeline": pipeline_name},
        )

        results = []
        for idx, step in enumerate(steps, start=1):
            role_label = step.get("role", "Dev")
            instruction = step.get("instruction", "")
            role = self._parse_role(role_label)

            message = self.bus.publish(
                sender="Manager",
                receiver=role.value,
                body=f"Etapa {idx}/{len(steps)}: {instruction}",
            )

            if not message["accepted"]:
                failure = {
                    "step": idx,
                    "status": "blocked",
                    "reason": message["reason"],
                }
                results.append(failure)
                self.memory.remember(
                    kind="pipeline_blocked",
                    content=f"Pipeline {pipeline_name} bloqueada por loop na etapa {idx}.",
                    metadata=failure,
                )
                return {"status": "blocked", "results": results}

            print(f"\n[Pipeline {pipeline_name}] Etapa {idx}: {role.value}")
            print(f"Instrucao: {instruction}")
            if self.bridge.interactive:
                approve = input("Aprova executar esta etapa? (s/n) [s]: ").strip().lower() or "s"
            else:
                approve = "s"
            if approve not in {"s", "sim", "y", "yes"}:
                skipped = {"step": idx, "status": "skipped", "instruction": instruction}
                results.append(skipped)
                self.memory.remember(
                    kind="pipeline_step_skipped",
                    content=f"Etapa {idx} pulada pelo dev.",
                    metadata=skipped,
                )
                continue

            result = self.bridge.sync_squad_intent(role, instruction)
            result_line = {
                "step": idx,
                "instruction": instruction,
                "role": role.value,
                "final_status": result.get("final_status", result.get("status", "unknown")),
            }
            if result.get("deliverable_file"):
                result_line["deliverable_file"] = result["deliverable_file"]
            results.append(result_line)

            self.memory.remember(
                kind="pipeline_step_result",
                content=(
                    f"Pipeline {pipeline_name} etapa {idx} ({role.value}) "
                    f"status {result_line['final_status']}."
                ),
                metadata=result_line,
            )

            if result_line["final_status"] in {"failed", "error", "exception"}:
                self.memory.remember(
                    kind="pipeline_failed",
                    content=f"Pipeline {pipeline_name} interrompida na etapa {idx}.",
                    metadata=result_line,
                )
                return {"status": "failed", "results": results}

        self.memory.remember(
            kind="pipeline_completed",
            content=f"Pipeline {pipeline_name} concluida.",
            metadata={"pipeline": pipeline_name, "steps": len(steps)},
        )
        return {"status": "completed", "results": results}

    def _run_parallel_command(self, command: str) -> dict:
        allowed, policy_msg = self.bridge.policies.pre_execution(command)
        if not allowed:
            return {
                "command": command,
                "status": "blocked",
                "stdout": "",
                "stderr": policy_msg,
                "return_code": -1,
            }

        result = self.bridge.executor.execute_command(command)
        return {
            "command": command,
            "status": result.get("status", "unknown"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "return_code": result.get("return_code", 1),
        }

    def run_parallel_commands(
        self,
        pipeline_name: str,
        commands: list[str],
        max_workers: int = 3,
    ) -> dict:
        filtered = [cmd.strip() for cmd in commands if cmd.strip()]
        if not filtered:
            return {"status": "empty", "results": [], "merged": {}}

        self.memory.remember(
            kind="parallel_pipeline_start",
            content=f"Pipeline paralela {pipeline_name} iniciada com {len(filtered)} comandos.",
            metadata={"pipeline": pipeline_name, "commands": len(filtered)},
        )

        with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(filtered)))) as executor:
            futures = [executor.submit(self._run_parallel_command, command) for command in filtered]
            results = [future.result() for future in futures]

        success_count = sum(1 for item in results if item["status"] == "success")
        blocked_count = sum(1 for item in results if item["status"] == "blocked")
        error_count = len(results) - success_count - blocked_count

        merged_stdout = "\n".join(
            [f"$ {item['command']}\n{item['stdout']}" for item in results if item.get("stdout")]
        ).strip()
        merged_stderr = "\n".join(
            [f"$ {item['command']}\n{item['stderr']}" for item in results if item.get("stderr")]
        ).strip()

        status = "completed" if error_count == 0 else "failed"
        merged = {
            "success": success_count,
            "blocked": blocked_count,
            "errors": error_count,
            "stdout": merged_stdout,
            "stderr": merged_stderr,
        }

        self.memory.remember(
            kind="parallel_pipeline_finished",
            content=(
                f"Pipeline paralela {pipeline_name} finalizada com "
                f"{success_count} sucesso, {blocked_count} bloqueados, {error_count} erros."
            ),
            metadata={"pipeline": pipeline_name, "merged": merged},
        )

        return {"status": status, "results": results, "merged": merged}
