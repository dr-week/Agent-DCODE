# Agent-DCODE Codebase Symbol Map

Auto-generated via `scripts/repomap_sync.py` using AST and Tree-Sitter.
Used by SWE agents and the Agent Harness to locate target symbols without overflowing context.

---

# Repository Symbol Map (74 files)

## dcode/agents/autonomous.py
  - class ModelType []
  - class AutonomousAgent [__init__, run, _fail_step]
  - def run_autonomous_agent(goal, project_name, max_iterations, context)

## dcode/agents/codex.py
  - class CodexAgent [__init__, execute_task, get_execution_log]
  - def get_agent()
  - def execute_task(task, context)

## dcode/agents/planner.py
  - def _serialize_context(context)
  - def generate_plan(goal, context)
  - def generate_actions(goal, plan, context)

## dcode/agents/prompts.py
  - def build_plan_prompt(goal, context)
  - def build_actions_prompt(goal, plan, context)

## dcode/agents/verifier.py
  - def execute_and_verify(actions)
  - def check_goal_complete(execution_result, success_criteria)

## dcode/archetypes/software_team.py
  - def create_software_team(team_name, llm_fn)

## dcode/archetypes/templates.py
  - def create_coding_agent_spec(name)
  - def create_research_agent_spec(name)
  - def create_data_analyst_spec(name)
  - def create_devops_sre_spec(name)
  - def create_security_auditor_spec(name)
  - def create_quantum_engineer_spec(name)
  - def list_archetypes()

## dcode/cli_anything/generator.py
  - def analyze_python_module(source_path)
  - def build_cli_harness_code(module_stem, functions)
  - def generate_cli_anything_harness(target_rel_path)

## dcode/cli_anything/runner.py
  - def discover_cli_harnesses()
  - def run_cli_harness(command, ensure_json)
  - def check_binary_available(binary_name)

## dcode/cli_anything/session.py
  - def _load_session()
  - def _save_session(state)
  - def record_snapshot(file_path, command)
  - def undo_last_mutation()
  - def get_session_status()

## dcode/cli_anything/skill_doc.py
  - def generate_skill_markdown(app_name, cli_filename, functions)

## dcode/context/builder.py
  - def prepare_agent_context(task, selected_code, active_file, project_dir)
  - def format_context_for_llm(context)

## dcode/context/extractors.py
  - def get_file_context(file_path, max_lines)
  - def get_directory_context(dir_path, max_depth)
  - def get_selected_code_context(code, language)

## dcode/framework/core/registry_loader.py
  - def load_agent_spec_from_dict(data)
  - def load_agent_spec_from_file(path)

## dcode/framework/core/spec.py
  - class AgentSpec [build_system_instructions]
  - class TaskSpec []

## dcode/framework/core/state_graph.py
  - class StateGraph [__init__, add_node, add_edge, add_conditional_edges, run]

## dcode/framework/core/tool_decorator.py
  - class ToolDefinition [__init__, _build_schema, __call__, invoke, to_dict]
  - def tool(func)

## dcode/framework/loops/react_loop.py
  - class ReActAgent [__init__, _build_prompt, run]

## dcode/framework/loops/reflexion_loop.py
  - class ReflexionAgent [__init__, _generate_draft, _critique_draft, run]

## dcode/framework/loops/swe_loop.py
  - class SWELoop [__init__, solve_issue, _run_verification]

## dcode/framework/loops/swe_patcher.py
  - class SWEPatcher [__init__, generate_and_apply]

## dcode/framework/swarm/multi_agent.py
  - class MultiAgentTeam [__init__, _instantiate, run]

## dcode/guardrails/approval.py
  - class ApprovalGate [__init__, requires_approval, request_approval]

## dcode/guardrails/policy.py
  - class GuardrailPolicy [validate_action, validate_batch]

## dcode/harness/benchmark_runner.py
  - class BenchmarkRunner [__init__, run_benchmark_suite]

## dcode/harness/config.py
  - class HarnessConfig [validate]

## dcode/harness/grader.py
  - class HarnessGrader [__init__, grade_command, grade_assertions]

## dcode/harness/guardian.py
  - class BudgetExceededError []
  - class StepCapExceededError []
  - class TimeoutExceededError []
  - class HarnessGuardian [__init__, tick_step, check_timeout, get_metrics]

## dcode/harness/runner.py
  - class AgentHarness [__init__, execute_swe_task]

## dcode/harness/scorecard.py
  - class HarnessScorecard [calculate, render_markdown]

## dcode/harness/trajectory.py
  - class TrajectoryRecorder [__init__, log_step, read_trajectory]

## dcode/harness/validator.py
  - class HarnessValidator [__init__, validate_python_syntax, validate_workspace_files]

## dcode/harness/workflow.py
  - class PipelineStage [__init__, run]
  - class HarnessPipeline [__init__, add_stage, execute]

## dcode/integrations/browser_tool.py
  - def inspect_html_dom(raw_html)
  - def browser_verify(url, expected_texts)

## dcode/integrations/cli_workflows.py
  - def run_fix_workflow(issue, repo_dir, test_cmd, max_attempts, model)
  - def run_research_workflow(url, prompt, user_id, model)
  - def run_qa_workflow(url, expect_texts)

## dcode/integrations/crawl4ai_tool.py
  - def html_to_markdown(raw_html)
  - def crawl_url(url, max_chars)

## dcode/integrations/langfuse_tracer.py
  - class LangfuseTracer [__init__, _init_db, record_span, summary]

## dcode/integrations/litellm_router.py
  - class LiteLLMRouter [__init__, complete, _record]

## dcode/integrations/mcp_bridge.py
  - class MCPBridge [__init__, _register_defaults, register_function, list_mcp_tools, call_mcp_tool]

## dcode/integrations/mem0_store.py
  - class Mem0Store [__init__, _init_sqlite, remember, recall]

## dcode/integrations/quantum_engine.py
  - class QuantumSimulator [__init__, apply_h, apply_x, apply_cnot, probabilities]
  - def simulate_quantum_circuit(num_qubits, gates)
  - def quantum_optimize_qubo(qubo_matrix, steps)

## dcode/integrations/registry.py
  - def get_integration_status()

## dcode/integrations/repomap.py
  - class RepoMap [__init__, scan, render_markdown, _extract_py, _extract_js]
  - def build_repo_map(root_dir)

## dcode/llm/colab_server.py
  - def agent_endpoint()
  - def health_endpoint()
  - def start_colab_server(port, use_ngrok)

## dcode/llm/gemini_client.py
  - class ColabAgentError []
  - def check_environment()
  - def check_memory()
  - def build_colab_prompt(task, code)
  - def call_gemini(prompt, model)

## dcode/llm/ollama_client.py
  - def _post_json(url, payload, timeout)
  - def ask_llm(user_input, model)
  - def ask_llm_structured(prompt, model)

## dcode/llm/parser.py
  - def extract_json(text)

## dcode/memory/episodic.py
  - class EpisodicMemory [__init__, _load, _save, record_episode, recall_similar]

## dcode/memory/semantic_rag.py
  - class SemanticMemory [__init__, _tokenize, add_document, search]

## dcode/memory/working.py
  - class WorkingMemory [__init__, add_message, set_var, get_var, format_prompt_history, clear]

## dcode/observability/log_formatter.py
  - def get_last_state(project)
  - def get_context_for_project(project, limit)
  - def format_log_summary(project)

## dcode/observability/log_store.py
  - def ensure_logs_dir()
  - def get_log_path(project)
  - def read_logs(project)
  - def write_log(project, task, action, status, details)
  - def clear_logs(project)

## dcode/observability/transparency_session.py
  - def get_tracker()
  - def create_new_session()
  - def reset_tracker()

## dcode/observability/transparency_tracker.py
  - class StepStatus []
  - class TransparencyTracker [__init__, start_execution, add_plan, start_step, add_action, complete_action, complete_step, add_error, complete_execution, get_state]

## dcode/orchestrator/health.py
  - def is_port_open(port, timeout)
  - def check_service_health(services, service_name)

## dcode/orchestrator/lifecycle.py
  - def start_backend_service(services, project_root, backend_script, log_fn)
  - def start_ollama_service(services, log_fn)
  - def stop_named_service(services, service_name, log_fn)

## dcode/orchestrator/manager.py
  - class Orchestrator [__init__, log, is_port_open, check_service_health, start_backend, start_ollama, start_all, stop_service, stop_all, restart_service, get_status, print_status, health_check_loop, run_health_check_background]
  - def start_all()
  - def stop_all()
  - def get_status()

## dcode/orchestrator/models.py
  - class ServiceStatus []
  - class Service []

## dcode/orchestrator/processes.py
  - def get_process_by_port(port)
  - def get_duplicate_processes(service_name)
  - def kill_duplicate_processes(service_name, log_fn)

## dcode/runtime/git_checkpoint.py
  - class GitCheckpoint [__init__, snapshot, diff_since, rollback, git_status]

## dcode/tools/code_tools.py
  - def run_cmd(a)
  - def run_python(a)
  - def run_bash(a)
  - def run_js(a)

## dcode/tools/edit_tools.py
  - def replace_in_file(a)
  - def search_code(a)

## dcode/tools/executor.py
  - def execute_actions(actions, dry_run)

## dcode/tools/file_tools.py
  - def safe_path(path)
  - def write_file(a)
  - def append_file(a)
  - def read_file(a)
  - def list_files(a)

## dcode/tools/system_tools.py
  - def get_processes(a)
  - def show_progress(a)

## dcode/web/app.py
  - def create_app()
  - def run_server(host, port, debug)

## dcode/web/routes/agent_routes.py
  - def agent_execute()
  - def agent_autonomous()
  - def agent_log_endpoint()
  - def agent_clear()

## dcode/web/routes/chat_routes.py
  - def run_single_prompt_agent(user_input)
  - def api_ask()
  - def api_history()
  - def api_clear()
  - def health()
  - def api_status()

## dcode/web/routes/cli_anything_routes.py
  - def list_harnesses()
  - def generate_harness()
  - def execute_harness()
  - def session_status()
  - def session_undo()

## dcode/web/routes/file_routes.py
  - def _build_tree(root_path, prefix)
  - def get_project_files()
  - def get_current_file()
  - def set_current_file()

## dcode/web/routes/framework_routes.py
  - def get_archetypes()
  - def get_integrations_endpoint()
  - def get_mcp_tools_endpoint()
  - def get_repomap_endpoint()
  - def get_telemetry_metrics()
  - def run_custom_agent()
  - def run_team_endpoint()

## dcode/web/routes/log_routes.py
  - def get_project_logs(project)
  - def get_project_summary(project)
  - def list_all_logs()

## dcode/web/routes/transparency_routes.py
  - def transparency_start_session()
  - def transparency_get_state()
  - def transparency_add_plan()
  - def transparency_start_step()
  - def transparency_complete_step()
  - def transparency_add_action()
  - def transparency_complete_action(action_index)
  - def transparency_report_error()
  - def transparency_complete_execution()

## dcode/web/static/script.js
  - function initCodexBar()
  - function handleAddFile()
  - function handleFileSelection(e)
  - function updateFilesIndicator()
  - function handleCodeContext()
  - function toggleSettingsPopup()
  - function showSettingsPopup()
  - function hideSettingsPopup()
  - function buildCodexRequest()
  - function sendCodexTask()
  - function initFilePanel()
  - function loadFileTree()
  - function renderFileTree()
  - function renderFileItem(item, level = 0)
  - function getFileIcon(filename)
  - function startFileStatusUpdate()
  - function updateFileStatus()
  - function highlightCurrentFile()
  - function clearCurrentFileHighlight()
  - function updateFileStatusIndicator(filePath, status)
  - class
        statusEl
  - function toggleSidebar()
  - function handleWindowResize()
  - function switchMode(mode)
  - function executeAgentTask()