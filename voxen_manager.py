import json
from datetime import datetime
from enum import Enum
from pathlib import Path


class AgentRole(Enum):
    MANAGER = "Manager"
    DEVELOPER = "Dev"
    QA = "Tester"
    GROWTH = "Growth"


class VoxenManager:
    """
    O Cérebro do Squad: orquestra tarefas e mantém o estado persistente.
    Inspirado em OpenAgents Control e arquitetura Voxen.
    """

    def __init__(self, state_file: str = "voxen_state.json") -> None:
        self.state_file = Path(state_file)
        self.state = self.load_state()

    def _default_state(self) -> dict:
        return {
            "project_name": "OpenCode_Alpha",
            "current_sprint": 1,
            "sprint_goal": "",
            "approvals": [],
            "tasks": [],
            "history": [],
        }

    def load_state(self) -> dict:
        if not self.state_file.exists():
            return self._default_state()
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self._default_state()

    def save_state(self) -> None:
        self.state_file.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    def add_task(self, description: str, role: AgentRole) -> dict:
        task = {
            "id": len(self.state["tasks"]) + 1,
            "description": description,
            "assigned_to": role.value,
            "status": "pending",
            "checkpoints": [],
            "created_at": datetime.now().isoformat(),
        }
        self.state["tasks"].append(task)
        self.state["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_id": task["id"],
                "event": "task_created",
                "log": f"Tarefa criada para {role.value}.",
            }
        )
        self.save_state()
        return task

    def set_sprint_goal(self, goal: str) -> None:
        self.state["sprint_goal"] = goal
        self.state["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_id": None,
                "event": "sprint_goal_updated",
                "log": goal,
            }
        )
        self.save_state()

    def add_checkpoint(self, task_id: int, checkpoint_name: str, required_by: str = "dev") -> bool:
        for task in self.state["tasks"]:
            if task["id"] == task_id:
                checkpoint = {
                    "name": checkpoint_name,
                    "required_by": required_by,
                    "approved": False,
                    "approved_at": None,
                }
                task["checkpoints"].append(checkpoint)
                self.state["history"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "task_id": task_id,
                        "event": "checkpoint_added",
                        "log": f"{checkpoint_name} ({required_by})",
                    }
                )
                self.save_state()
                return True
        return False

    def approve_checkpoint(self, task_id: int, checkpoint_name: str, approver: str = "dev") -> bool:
        for task in self.state["tasks"]:
            if task["id"] != task_id:
                continue
            for checkpoint in task.get("checkpoints", []):
                if checkpoint["name"] == checkpoint_name and checkpoint["required_by"] == approver:
                    checkpoint["approved"] = True
                    checkpoint["approved_at"] = datetime.now().isoformat()
                    self.state["history"].append(
                        {
                            "timestamp": checkpoint["approved_at"],
                            "task_id": task_id,
                            "event": "checkpoint_approved",
                            "log": checkpoint_name,
                        }
                    )
                    self.save_state()
                    return True
        return False

    def list_tasks(self, status: str | None = None) -> list[dict]:
        if status is None:
            return list(self.state["tasks"])
        return [task for task in self.state["tasks"] if task.get("status") == status]

    def create_approval(self, task_id: int, stage: str, summary: str) -> dict:
        approval = {
            "id": len(self.state["approvals"]) + 1,
            "task_id": task_id,
            "stage": stage,
            "summary": summary,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
        }
        self.state["approvals"].append(approval)
        self.state["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "event": "approval_created",
                "log": f"{stage}: {summary}",
            }
        )
        self.save_state()
        return approval

    def update_approval(self, approval_id: int, status: str) -> bool:
        for item in self.state["approvals"]:
            if item["id"] == approval_id:
                item["status"] = status
                if status == "approved":
                    item["approved_at"] = datetime.now().isoformat()
                self.state["history"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "task_id": item["task_id"],
                        "event": "approval_updated",
                        "log": f"{item['stage']} => {status}",
                    }
                )
                self.save_state()
                return True
        return False

    def update_task_status(self, task_id: int, status: str, log_msg: str = "") -> bool:
        for task in self.state["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                self.state["history"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "task_id": task_id,
                        "event": f"status_changed_to_{status}",
                        "log": log_msg,
                    }
                )
                self.save_state()
                return True
        return False


# Inicializando o Cérebro
manager = VoxenManager()
