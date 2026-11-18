"""
Flask route blueprints registry.
"""

from dcode.web.routes.agent_routes import agent_bp
from dcode.web.routes.chat_routes import chat_bp
from dcode.web.routes.cli_anything_routes import cli_anything_bp
from dcode.web.routes.file_routes import file_bp
from dcode.web.routes.framework_routes import framework_bp
from dcode.web.routes.log_routes import log_bp
from dcode.web.routes.transparency_routes import transparency_bp

ALL_BLUEPRINTS = (
    chat_bp,
    agent_bp,
    file_bp,
    log_bp,
    transparency_bp,
    cli_anything_bp,
    framework_bp,
)

__all__ = ["ALL_BLUEPRINTS"]
