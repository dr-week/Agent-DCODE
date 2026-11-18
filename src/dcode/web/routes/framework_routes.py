"""
Universal Agentic Framework REST API routes (/api/framework/*).
Allows inspecting archetypes, dynamically instantiating custom agents, and running multi-agent teams.
"""

from flask import Blueprint, jsonify, request
from dcode.archetypes import ARCHETYPE_CATALOG, create_software_team, list_archetypes
from dcode.framework import ReActAgent, ReflexionAgent, load_agent_spec_from_dict

framework_bp = Blueprint("framework", __name__)


@framework_bp.route("/api/framework/archetypes", methods=["GET"])
def get_archetypes():
    """List all pre-built agent archetypes available in the framework."""
    items = list_archetypes()
    return jsonify({"archetypes": items, "count": len(items)})


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
    """Run the 3-agent Software Engineering Team (Architect → Developer → QA Critic)."""
    data = request.json or {}
    objective = data.get("objective", "").strip()
    if not objective:
        return jsonify({"success": False, "error": "'objective' is required"}), 400

    team = create_software_team()
    return jsonify(team.run(objective))
