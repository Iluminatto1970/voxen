import re
from pathlib import Path

from memory_hub import MemoryHub
from message_bus import MessageBus
from pipeline_runner import PipelineRunner
from skills_catalog import SkillsCatalog
from strategic_triage import StrategicTriage
from voxen_blueprints import get_blueprints
from voxen_brainstorm import BrainstormAgent
from voxen_bridge import VoxenBridge
from voxen_bundles import VoxenBundles
from voxen_context import VoxenContextEngine
from voxen_manager import AgentRole
from voxen_orchestrator import VoxenOrchestrator
from voxen_profiles import VoxenModelProfiles
from voxen_registry import VoxenRegistry
from voxen_router import VoxenIntentRouter
from voxen_specialists import VoxenSpecialists
from voxen_workflows import VoxenWorkflows


def choose_role() -> AgentRole:
    roles = {
        "1": AgentRole.MANAGER,
        "2": AgentRole.DEVELOPER,
        "3": AgentRole.QA,
        "4": AgentRole.GROWTH,
    }
    print("\nEscolha o agente responsável:")
    print("1) Manager")
    print("2) Dev")
    print("3) Tester")
    print("4) Growth")
    choice = (input("Opção [2]: ").strip() or "2").lower()
    return roles.get(choice, AgentRole.DEVELOPER)


def run_mode_pipeline(mode_name: str, runner: PipelineRunner) -> None:
    steps = get_blueprints().get(mode_name, [])
    if not steps:
        print(f"Nenhum blueprint configurado para {mode_name}.\n")
        return
    result = runner.run(pipeline_name=f"pipeline_{mode_name}", steps=steps)
    print("\nResultado do pipeline:")
    print(result)
    print()


def create_isolated_workspace(workspace_dir: str, task_label: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", task_label.strip().lower()).strip("-") or "task"
    target = Path(f"{workspace_dir}/_worktrees/{slug}")
    target.mkdir(parents=True, exist_ok=True)
    return str(target)


def init_project_voxen(project_dir: str) -> str:
    project_path = Path(project_dir).expanduser().resolve()
    target_dir = project_path / ".voxen"
    bin_dir = target_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent
    auto_update_helper = root.parent / "bin" / "voxen_auto_update.sh"
    launcher = bin_dir / "voxen"
    launcher.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"if [[ -x \"{auto_update_helper}\" ]]; then\n"
        f"  \"{auto_update_helper}\" || true\n"
        "fi\n"
        f"exec python3 \"{root / 'voxen.py'}\" \"$@\"\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    install_opencode_voxen_command(project_path)
    return str(target_dir)


def install_opencode_voxen_command(project_path: Path) -> str:
    commands_dir = project_path / ".opencode" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    command_file = commands_dir / "voxen.md"
    command_file.write_text(
        "---\n"
        "description: Executa comandos do Voxen CLI\n"
        "---\n"
        "Voce esta operando o comando '/voxen' no projeto.\n\n"
        "Regras de execucao:\n\n"
        "1) Para fluxos estilo antigravity (interacao conversacional), quando '$ARGUMENTS'\n"
        "comecar com um destes subcomandos:\n"
        "- 'brainstorm'\n"
        "- 'plan'\n"
        "- 'create'\n"
        "- 'debug'\n"
        "- 'enhance'\n"
        "- 'preview'\n"
        "- 'orchestrate'\n"
        "- 'test'\n"
        "- 'deploy'\n"
        "- 'workflow'\n\n"
        "Comporte-se como workflow guiado: converse com o usuario, faca perguntas curtas\n"
        "de contexto quando faltarem dados, apresente opcoes com tradeoffs e recomende\n"
        "proximo passo. Nao gerar codigo na primeira resposta desse fluxo.\n\n"
        "Formato esperado para brainstorm/plan (padrao antigravity):\n\n"
        "```markdown\n"
        "## 🧠 Brainstorm: [Topico]\n\n"
        "### Context\n"
        "[Resumo do problema]\n\n"
        "---\n\n"
        "### Option A: [Nome]\n"
        "...\n\n"
        "✅ **Pros:**\n"
        "- ...\n\n"
        "❌ **Cons:**\n"
        "- ...\n\n"
        "📊 **Effort:** Low | Medium | High\n\n"
        "---\n\n"
        "### Option B: [Nome]\n"
        "...\n\n"
        "### Option C: [Nome]\n"
        "...\n\n"
        "## 💡 Recommendation\n\n"
        "**Option [X]** because [reasoning].\n\n"
        "What direction would you like to explore?\n"
        "```\n\n"
        "2) Para subcomandos operacionais (status, skills, list, context, route etc),\n"
        "execute o Voxen CLI e resuma o resultado de forma objetiva.\n\n"
        "!`./.voxen/bin/voxen --cmd \"/voxen $ARGUMENTS\"`\n",
        encoding="utf-8",
    )
    return str(command_file)


def print_voxen_suggestions(
    mode_name: str,
    context_engine: VoxenContextEngine,
    catalog: SkillsCatalog,
    workflows: VoxenWorkflows,
    router: VoxenIntentRouter,
    intent: str = "",
) -> None:
    snapshot = context_engine.load_snapshot() or context_engine.analyze()
    recommended = catalog.recommend(mode_name=mode_name, intent=intent, limit=8)
    labels = catalog.format_skill_labels(recommended)
    print("\nSugestoes Voxen:")
    print(f"- modo ativo: {mode_name}")
    print(f"- stack detectada: {', '.join(snapshot['stack']) if snapshot['stack'] else 'desconhecida'}")
    print(f"- workflows uteis: {', '.join(workflows.names())}")
    print(f"- skills sugeridas: {', '.join(labels) if labels else 'nenhuma'}")
    if intent:
        route = router.route(intent)
        print(
            f"- rota: role={route['role'].value}, workflow={route['workflow']}, "
            f"skill={route['skill']}, specialist={route.get('specialist', '')}"
        )
    print()


def run_brainstorm_session(
    mode_name: str,
    workspace_dir: str,
    intent: str = "",
    interactive: bool = True,
) -> None:
    if interactive and not intent:
        intent = input("Topico para brainstorm: ").strip()

    if not intent:
        print("Missao vazia. Use /voxen brainstorm <texto>.\n")
        return

    agent = BrainstormAgent(project_name=f"{mode_name}_project", workspace_dir=workspace_dir)
    blueprint = agent.define_mission(user_intent=intent, mode="BRUTAL")
    report = blueprint.get("brainstorm_report", "")
    print()
    if report:
        print(report)
    else:
        print("Blueprint gerado:")
        print(blueprint)
    print()


def voxen_help() -> None:
    print("\nComandos /voxen disponiveis:")
    print("/voxen")
    print("/voxen help")
    print("/voxen list")
    print("/voxen create")
    print("/voxen create <texto>")
    print("/voxen run <nome>")
    print("/voxen run-current")
    print("/voxen skills")
    print("/voxen install <skill>")
    print("/voxen uninstall <skill>")
    print("/voxen skills validate")
    print("/voxen skills lock")
    print("/voxen skills pin <skill@versao>")
    print("/voxen skills unpin <skill>")
    print("/voxen skills health")
    print("/voxen skills heal")
    print("/voxen skills enforce")
    print("/voxen skills sync-pins")
    print("/voxen context")
    print("/voxen context domains")
    print("/voxen workflows")
    print("/voxen workflow <nome> <texto>")
    print("/voxen plan <texto>")
    print("/voxen enhance <texto>")
    print("/voxen preview <texto>")
    print("/voxen orchestrate <texto>")
    print("/voxen debug <texto>")
    print("/voxen test <texto>")
    print("/voxen deploy <texto>")
    print("/voxen parallel <cmd1 || cmd2 || ...>")
    print("/voxen route <texto>")
    print("/voxen suggest <texto>")
    print("/voxen bundle")
    print("/voxen bundle install")
    print("/voxen scout <texto>")
    print("/voxen eval summary")
    print("/voxen status")
    print("/voxen profiles")
    print("/voxen specialists")
    print("/voxen brainstorm")
    print("/voxen brainstorm <texto>")
    print("/voxen isolate <nome>")
    print("/voxen policy check <comando>")
    print("/voxen init [caminho]")
    print()


def bootstrap_runtime(interactive: bool = True) -> dict:
    root = Path(__file__).resolve().parent
    triage = StrategicTriage()
    orchestrator = VoxenOrchestrator()
    mode_lookup = {
        "MICRO_SAAS": "micro_saas",
        "DEV_TOOL_CLI": "dev_tool_cli",
        "SUPPORT_AGENT": "support_agent",
        "MVP_GENERIC": "micro_saas",
    }
    lock_data = triage.load_lock()
    if lock_data and not lock_data.get("first_deploy_completed", False):
        mode_name = mode_lookup.get(lock_data.get("mode", "MICRO_SAAS"), "micro_saas")
    else:
        if interactive:
            selected_mode, instruction = triage.ask_strategy()
            triage.save_lock(selected_mode, instruction)
            mode_name = mode_lookup.get(selected_mode, "micro_saas")
        else:
            mode_name = "micro_saas"

    orchestrator.deploy_war_room(mode_name)
    workspace_dir = str(orchestrator.get_workspace_for_mode(mode_name))
    state_file = orchestrator.get_state_file_for_mode(mode_name)
    bridge = VoxenBridge(workspace_dir=workspace_dir, state_file=state_file, interactive=interactive)
    runner = PipelineRunner(
        bridge=bridge,
        message_bus=MessageBus(bus_file=f"{workspace_dir}/message_bus.json"),
        memory_hub=MemoryHub(memory_file=f"{workspace_dir}/_memory/memories.jsonl"),
    )
    context_engine = VoxenContextEngine(workspace_dir=workspace_dir)
    workflows = VoxenWorkflows()
    profiles = VoxenModelProfiles()
    registry = VoxenRegistry(squads_dir="squads")
    catalog = SkillsCatalog(
        source_root=str(root / "_references" / "antigravity-awesome-skills" / "skills"),
        source_roots=[
            str(Path.cwd() / ".agent" / "skills"),
            str(root / "_references" / "antigravity-kit" / ".agent" / "skills"),
            str(root / "_references" / "antigravity-awesome-skills" / "skills"),
        ],
        target_root="skills",
    )
    bundles = VoxenBundles(catalog=catalog)
    specialists = VoxenSpecialists(
        source_roots=[
            str(Path.cwd() / ".agent" / "agents"),
            str(root / "_references" / "antigravity-kit" / ".agent" / "agents"),
        ]
    )
    router = VoxenIntentRouter(specialists=specialists.list_specialists())
    bundles.install_bundle(mode_name, top_n=3)

    return {
        "triage": triage,
        "mode_name": mode_name,
        "workspace_dir": workspace_dir,
        "bridge": bridge,
        "runner": runner,
        "context_engine": context_engine,
        "router": router,
        "workflows": workflows,
        "profiles": profiles,
        "registry": registry,
        "catalog": catalog,
        "bundles": bundles,
        "specialists": specialists,
    }


def handle_voxen_command(
    raw_command: str,
    mode_name: str,
    runner: PipelineRunner,
    registry: VoxenRegistry,
    catalog: SkillsCatalog,
    bridge: VoxenBridge,
    context_engine: VoxenContextEngine,
    router: VoxenIntentRouter,
    workflows: VoxenWorkflows,
    profiles: VoxenModelProfiles,
    bundles: VoxenBundles,
    specialists: VoxenSpecialists,
    workspace_dir: str,
    allow_prompt: bool = True,
) -> None:
    command = raw_command.strip()
    if command in {"/voxen", "/voxen menu", "/voxen help"}:
        voxen_help()
        if command != "/voxen help":
            intent = input("Opcional: descreva sua intencao [enter para pular]: ").strip() if allow_prompt else ""
            print_voxen_suggestions(mode_name, context_engine, catalog, workflows, router, intent=intent)
        return

    if command == "/voxen list":
        squads = registry.list_squads()
        print("\nSquads cadastrados:" if squads else "Nenhum squad cadastrado ainda.")
        for name in squads:
            print(f"- {name}")
        print()
        return

    if command == "/voxen create":
        display_name = input("Nome do squad: ").strip()
        if not display_name:
            print("Nome invalido.\n")
            return
        description = input("Descricao: ").strip() or "Squad gerado via CLI"
        squad_dir = registry.create_squad(display_name, description, mode_name, get_blueprints().get(mode_name, []))
        print(f"Squad criado em {squad_dir}.\n")
        return
    if command.startswith("/voxen create "):
        intent = command.replace("/voxen create ", "", 1).strip() or "entrega solicitada"
        print(runner.run(pipeline_name="workflow_create", steps=workflows.build_steps("create", intent)))
        return

    if command.startswith("/voxen run "):
        name = command.replace("/voxen run ", "", 1).strip()
        squad = registry.load_squad(name)
        if not squad:
            print("Squad nao encontrado.\n")
            return
        print(runner.run(pipeline_name=f"squad_{squad['name']}", steps=squad.get("steps", [])))
        return

    if command == "/voxen run-current":
        run_mode_pipeline(mode_name, runner)
        return

    if command == "/voxen skills":
        print("\nSkills instaladas:")
        for label in catalog.format_skill_labels(catalog.list_installed()[:20]):
            print(f"- {label}")
        print()
        return

    if command.startswith("/voxen install "):
        name = command.replace("/voxen install ", "", 1).strip()
        ok, msg = catalog.install(name)
        print((msg if ok else f"Falha: {msg}") + "\n")
        return

    if command.startswith("/voxen uninstall "):
        name = command.replace("/voxen uninstall ", "", 1).strip()
        ok, msg = catalog.uninstall(name)
        print((msg if ok else f"Falha: {msg}") + "\n")
        return

    if command == "/voxen skills validate":
        print(catalog.validate_installed())
        return
    if command == "/voxen skills lock":
        print(catalog.lock_status())
        return
    if command.startswith("/voxen skills pin "):
        print(catalog.pin_skill(command.replace("/voxen skills pin ", "", 1).strip()))
        return
    if command.startswith("/voxen skills unpin "):
        print(catalog.unpin_skill(command.replace("/voxen skills unpin ", "", 1).strip()))
        return
    if command == "/voxen skills health":
        print(catalog.health_summary())
        return
    if command == "/voxen skills heal":
        print(catalog.heal_skills())
        return
    if command == "/voxen skills enforce":
        print(catalog.enforce_pins())
        return
    if command == "/voxen skills sync-pins":
        print(catalog.sync_pins())
        return

    if command == "/voxen context":
        print(context_engine.analyze())
        return
    if command == "/voxen context domains":
        print(context_engine.domain_context())
        return
    if command == "/voxen workflows":
        print(workflows.names())
        return
    if command.startswith("/voxen workflow "):
        payload = command.replace("/voxen workflow ", "", 1).strip()
        parts = payload.split(" ", 1)
        wf_name = parts[0].strip()
        intent = parts[1].strip() if len(parts) > 1 else "entrega solicitada"
        print(runner.run(pipeline_name=f"workflow_{wf_name}", steps=workflows.build_steps(wf_name, intent)))
        return
    if command.startswith("/voxen parallel "):
        commands = [c.strip() for c in command.replace("/voxen parallel ", "", 1).split("||") if c.strip()]
        print(runner.run_parallel_commands("parallel_commands", commands, max_workers=min(4, len(commands))))
        return

    for shortcut in ["plan", "enhance", "preview", "orchestrate", "debug", "test", "deploy", "create"]:
        prefix = f"/voxen {shortcut} "
        if command.startswith(prefix):
            intent = command.replace(prefix, "", 1).strip() or "entrega solicitada"
            print(runner.run(pipeline_name=f"workflow_{shortcut}", steps=workflows.build_steps(shortcut, intent)))
            return

    if command.startswith("/voxen route "):
        print(router.route(command.replace("/voxen route ", "", 1).strip()))
        return
    if command.startswith("/voxen suggest "):
        print_voxen_suggestions(mode_name, context_engine, catalog, workflows, router, intent=command.replace("/voxen suggest ", "", 1).strip())
        return
    if command == "/voxen bundle":
        print(bundles.list_bundle(mode_name))
        return
    if command == "/voxen bundle install":
        print(bundles.install_bundle(mode_name, top_n=5))
        return
    if command.startswith("/voxen scout "):
        print(specialists.parallel_scout(command.replace("/voxen scout ", "", 1).strip(), top_n=3))
        return
    if command == "/voxen eval summary":
        print(bridge.evaluator.summary())
        return
    if command == "/voxen status":
        print({
            "pending": len(bridge.manager.list_tasks("pending")),
            "in_progress": len(bridge.manager.list_tasks("in_progress")),
            "failed": len(bridge.manager.list_tasks("failed")),
            "completed": len(bridge.manager.list_tasks("completed")),
        })
        return
    if command == "/voxen profiles":
        print({name: profiles.describe(name) for name in profiles.list_profiles()})
        return
    if command == "/voxen specialists":
        print("\nEspecialistas disponiveis:")
        for specialist in specialists.list_specialists():
            print(f"- @{specialist['id']} ({specialist['workflow']}): {specialist['description']}")
        print()
        return
    if command == "/voxen brainstorm":
        run_brainstorm_session(mode_name, workspace_dir, interactive=allow_prompt)
        return
    if command.startswith("/voxen brainstorm "):
        intent = command.replace("/voxen brainstorm ", "", 1).strip()
        run_brainstorm_session(mode_name, workspace_dir, intent=intent, interactive=False)
        return
    if command.startswith("/voxen isolate "):
        print(create_isolated_workspace(workspace_dir, command.replace("/voxen isolate ", "", 1).strip()))
        return
    if command.startswith("/voxen policy check "):
        print(bridge.policies.pre_execution(command.replace("/voxen policy check ", "", 1).strip()))
        return
    if command == "/voxen init":
        print(init_project_voxen("."))
        return
    if command.startswith("/voxen init "):
        print(init_project_voxen(command.replace("/voxen init ", "", 1).strip()))
        return

    print("Comando /voxen nao reconhecido. Use /voxen help.\n")


def main() -> None:
    print("=== Voxen CLI ===")
    runtime = bootstrap_runtime(interactive=True)
    triage = runtime["triage"]
    mode_name = runtime["mode_name"]
    workspace_dir = runtime["workspace_dir"]
    bridge = runtime["bridge"]
    runner = runtime["runner"]
    context_engine = runtime["context_engine"]
    router = runtime["router"]
    workflows = runtime["workflows"]
    profiles = runtime["profiles"]
    registry = runtime["registry"]
    catalog = runtime["catalog"]
    bundles = runtime["bundles"]
    specialists = runtime["specialists"]
    memory = MemoryHub(memory_file=f"{workspace_dir}/_memory/memories.jsonl")

    print_voxen_suggestions(mode_name, context_engine, catalog, workflows, router)

    while True:
        print("Menu:")
        print("1) Criar/Executar tarefa")
        print("2) Rodar pipeline do modo atual")
        print("3) Comando /voxen")
        print("4) Buscar memoria")
        print("5) Marcar primeiro deploy concluido")
        print("6) Brainstorm")
        print("7) Sair")
        choice = input("Escolha [1]: ").strip() or "1"
        if choice == "2":
            run_mode_pipeline(mode_name, runner)
            continue
        if choice == "3":
            cmd = input("Digite o comando /voxen: ").strip()
            if cmd:
                handle_voxen_command(
                    cmd,
                    mode_name,
                    runner,
                    registry,
                    catalog,
                    bridge,
                    context_engine,
                    router,
                    workflows,
                    profiles,
                    bundles,
                    specialists,
                    workspace_dir,
                    allow_prompt=True,
                )
            continue
        if choice == "4":
            query = input("Buscar termo: ").strip()
            if query:
                print(memory.recall(query, limit=5))
            continue
        if choice == "5":
            triage.set_first_deploy_completed()
            print("Deploy inicial marcado.\n")
            continue
        if choice == "6":
            run_brainstorm_session(mode_name, workspace_dir, interactive=True)
            continue
        if choice == "7":
            print("Encerrando Voxen.")
            break

        instruction = input("Descreva a instrucao: ").strip()
        if not instruction:
            continue
        suggested = router.route(instruction)
        print(f"Roteamento automatico: {suggested}")
        role = suggested["role"] if input("Usar role sugerida? (s/n) [s]: ").strip().lower() in {"", "s", "sim", "y", "yes"} else choose_role()
        print(bridge.sync_squad_intent(role, instruction))


def run_single_command(raw_command: str) -> int:
    runtime = bootstrap_runtime(interactive=False)
    commands = [part.strip() for part in raw_command.replace("\n", ";;").split(";;") if part.strip()]
    for command in commands:
        handle_voxen_command(
            command,
            runtime["mode_name"],
            runtime["runner"],
            runtime["registry"],
            runtime["catalog"],
            runtime["bridge"],
            runtime["context_engine"],
            runtime["router"],
            runtime["workflows"],
            runtime["profiles"],
            runtime["bundles"],
            runtime["specialists"],
            runtime["workspace_dir"],
            allow_prompt=False,
        )
    return 0


if __name__ == "__main__":
    main()
