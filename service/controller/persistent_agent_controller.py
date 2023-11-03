"""This controller provides the persistent proxy agent blueprint."""

from time import time

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError
from structlog import get_logger

from entity.agent import PersistentAgentRequestPayload
from utils.agent_pool import AgentPool


def construct_persistent_agent_blueprint(agent_pool: AgentPool) -> Blueprint:
    """Construct the persistent agent blueprint."""

    log = get_logger(__name__)
    log.propagate = False
    ctrl = Blueprint("persistent-agent", __name__)

    @ctrl.before_request
    def before_request():
        request.start_time = time()

    @ctrl.route("/agent/persistent", methods=["POST", "DELETE"])
    @ctrl.route("/agent/persistent/<int:agent_id>", methods=["GET", "DELETE"])
    def agent_request(agent_id=None):
        """Manage proxy agents."""

        arp = PersistentAgentRequestPayload()
        params = {}
        if request.content_type == "application/json":
            pld = request.get_json()
            if pld is not None:
                try:
                    params = arp.load(pld)
                except ValidationError as err:
                    return jsonify(err.messages), 400

        if request.method == "GET":
            if agent_id is not None:
                if agent_id in agent_pool:
                    agent = agent_pool[agent_id]
                    cookies = agent.cookies.get_dict()
                    return (
                        jsonify(
                            {
                                "User-Agent": agent.headers.get("User-Agent", ""),
                                "cf_clearance": cookies.get("cf_clearance", ""),
                            }
                        ),
                        200,
                    )
                else:
                    return Response(status=404)
        elif request.method == "POST":
            try:
                agent_id, agent = agent_pool.generate(**params)
            except Exception as err:
                log.error("Couldn't create an agent.", error=err)
                return Response(status=500)
            return jsonify({"id": agent_id}), 200
        elif request.method == "DELETE":
            if agent_id is not None:
                agent_pool.pop(agent_id, None)
                return Response(status=200)
            else:
                agent_pool.clear()
                return Response(status=200)

    @ctrl.after_request
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

    return ctrl
