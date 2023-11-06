"""This controller provides the ephemeral proxy agent blueprint."""

from time import time
from urllib.parse import unquote

import cloudscraper
from entity.agent import (
    AgentRequestFullResponse,
    EphemeralAgentRequestData,
    EphemeralAgentRequestParams,
)
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from structlog import get_logger
from utils.dotdict import dotdict


def construct_ephemeral_agent_blueprint() -> Blueprint:
    log = get_logger(__name__)
    bp = Blueprint(
        "ephemeral-agent",
        __name__,
        url_prefix="/agent/ephemeral",
        description="Ephemeral agent API.",
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

    @bp.route("", methods=["POST"])
    @bp.arguments(EphemeralAgentRequestParams, location="query", required=True)
    @bp.arguments(EphemeralAgentRequestData, location="json", required=False)
    @bp.response(201, AgentRequestFullResponse)
    def create(params, data):
        """Generate an ephemeral agent: user agent and cloudflare session cookie."""

        params = dotdict(params)
        try:
            url = unquote(params.url)
            cookie, ua = cloudscraper.get_cookie_string(url, **data)
        except Exception as err:
            log.error("Couldn't create an ephemeral agent.", error=err)
            return abort(500)

        return (
            jsonify(
                {
                    "user_agent": ua,
                    "cf_clearance": cookie.lstrip("cf_clearance="),
                }
            ),
            201,
        )

    return bp
