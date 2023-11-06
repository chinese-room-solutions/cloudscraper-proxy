"""This controller provides the persistent proxy agent blueprint."""

from time import time

from entity.agent import (
    AgentRequestFullResponse,
    AgentRequestShortResponse,
    PersistentAgentRequestData,
)
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from structlog import get_logger
from utils.agent_pool import AgentPool


def construct_persistent_agent_blueprint(agent_pool: AgentPool) -> Blueprint:
    log = get_logger(__name__)
    bp = Blueprint(
        "persistent-agent",
        __name__,
        url_prefix="/agent/persistent",
        description="Persistent agent API.",
    )

    @bp.before_request
    def before_request():
        request.start_time = time()

    @bp.after_request
    def after_request(response):
        request_time = time() - request.start_time
        log.info(
            "Processing request.",
            endpoint=request.url_rule.rule,
            args=request.view_args,
            method=request.method,
            status=response.status_code,
            src=request.remote_addr,
            time_seconds=request_time,
        )
        return response

    @bp.route("/<int:agent_id>", methods=["GET"])
    @bp.response(200, AgentRequestFullResponse)
    def get(agent_id):
        """Get the persistent agent."""

        if agent_id in agent_pool:
            agent = agent_pool[agent_id]
            cookies = agent.cookies.get_dict()

            return (
                jsonify(
                    {
                        "user_agent": agent.headers.get("User-Agent", ""),
                        "cf_clearance": cookies.get("cf_clearance", ""),
                    }
                ),
                200,
            )
        else:
            return abort(404)

    @bp.route("", methods=["POST"])
    @bp.arguments(
        PersistentAgentRequestData,
        location="json",
        required=False,
    )
    @bp.response(201, AgentRequestShortResponse)
    def create(data):
        """Generate a persistent agent."""

        try:
            agent_id, _ = agent_pool.generate(**data)
        except Exception as err:
            log.error("Couldn't create an agent.", error=err)
            return abort(500)

        return jsonify({"id": agent_id}), 201

    @bp.route("/<int:agent_id>", methods=["DELETE"])
    @bp.response(200, AgentRequestShortResponse)
    def delete_one(agent_id):
        """Delete the persistent agent by the Id."""

        if agent_id not in agent_pool:
            return abort(404)
        agent_pool.pop(agent_id, None)
        return jsonify({"id": agent_id}), 200

    @bp.route("", methods=["DELETE"])
    @bp.response(
        200,
        schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
        },
    )
    def delete_all():
        """Delete all persistent agents."""

        agent_pool.clear()
        return jsonify({"message": "All agents deleted"}), 200

    return bp
