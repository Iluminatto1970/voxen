from voxen_context import VoxenContextEngine
from voxen_router import VoxenIntentRouter


def run_quick_eval(workspace_dir: str) -> dict:
    router = VoxenIntentRouter()
    context = VoxenContextEngine(workspace_dir=workspace_dir)

    intents = [
        "debug erro no login",
        "criar endpoint backend para checkout",
        "rodar deploy em producao",
        "planejar sprint de onboarding",
    ]
    routes = [router.route(intent) for intent in intents]
    snapshot = context.analyze()

    return {
        "routes": [
            {
                "intent": intents[idx],
                "role": routes[idx]["role"].value,
                "workflow": routes[idx]["workflow"],
                "skill": routes[idx]["skill"],
            }
            for idx in range(len(intents))
        ],
        "files_count": snapshot["files_count"],
        "stack": snapshot["stack"],
    }


if __name__ == "__main__":
    result = run_quick_eval("workspace")
    print(result)
