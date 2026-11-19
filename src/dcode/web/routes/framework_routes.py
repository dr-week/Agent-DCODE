"""
Universal Agentic Framework & Open-Source Integrations REST API (/api/framework/*).
Allows inspecting archetypes, open-source integrations, MCP tools, RepoMap, and telemetry.
"""

from flask import Blueprint, jsonify, request
from dcode.archetypes import ARCHETYPE_CATALOG, create_software_team, list_archetypes
from dcode.config import PROJECTS_DIR
from dcode.framework import ReActAgent, ReflexionAgent, load_agent_spec_from_dict
from dcode.integrations import LangfuseTracer, MCPBridge, build_repo_map, get_integration_status

framework_bp = Blueprint("framework", __name__)


@framework_bp.route("/api/framework/archetypes", methods=["GET"])
def get_archetypes():
    """List all pre-built agent archetypes available in the framework."""
    items = list_archetypes()
    return jsonify({"archetypes": items, "count": len(items)})


@framework_bp.route("/api/framework/integrations", methods=["GET"])
def get_integrations_endpoint():
    """List all 8 open-source GitHub project integrations and their live status."""
    items = get_integration_status()
    return jsonify({"integrations": items, "count": len(items)})


@framework_bp.route("/api/framework/mcp/tools", methods=["GET"])
def get_mcp_tools_endpoint():
    """Return MCP-standard tool definitions exposed by Agent-DCODE's FastMCP bridge."""
    bridge = MCPBridge()
    return jsonify({"server": bridge.server_name, "tools": bridge.list_mcp_tools()})


@framework_bp.route("/api/framework/repomap", methods=["GET"])
def get_repomap_endpoint():
    """Generate an AST & Tree-Sitter repository symbol map for the workspace."""
    target = request.args.get("dir", PROJECTS_DIR)
    return jsonify(build_repo_map(target))


@framework_bp.route("/api/framework/metrics", methods=["GET"])
def get_telemetry_metrics():
    """Return aggregate token, cost, and latency metrics from LangfuseTracer."""
    tracer = LangfuseTracer()
    return jsonify(tracer.summary())


@framework_bp.route("/api/framework/run-agent", methods=["POST"])
def run_custom_agent():
    """Instantiate and run any custom agent from a JSON spec or archetype name."""
    data = request.json or {}
    task = data.get("task", "").strip()
    if not task:
        return jsonify({"success": False, "error": "'task' is required"}), 400

    archetype_key = data.get("archetype")
    if archetype_key and archetype_key in ARCHETYPE_CATALOG:
        spec = ARCHETYPE_CATALOG[archetype_key]()
    else:
        spec = load_agent_spec_from_dict(data.get("spec") or data)

    runner = ReflexionAgent(spec) if spec.loop_type == "reflexion" else ReActAgent(spec)
    return jsonify(runner.run(task))


@framework_bp.route("/api/framework/run-team", methods=["POST"])
def run_team_endpoint():
    """Run the 3-agent Software Engineering Team (Architect -> Developer -> QA Critic)."""
    data = request.json or {}
    objective = data.get("objective", "").strip()
    if not objective:
        return jsonify({"success": False, "error": "'objective' is required"}), 400

    team = create_software_team()
    return jsonify(team.run(objective))
