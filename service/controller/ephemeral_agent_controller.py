"""This controller provides the ephemeral proxy agent blueprint."""

from time import time
from urllib.parse import unquote

import cloudscraper
from entity.agent import EphemeralAgentRequest, EphemeralAgentRequestPayload
from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError
from structlog import get_logger
from utils.dotdict import dotdict


def construct_ephemeral_agent_blueprint() -> Blueprint:
    """Construct the ephemeral agent blueprint."""

    log = get_logger(__name__)
    ctrl = Blueprint("ephemeral-agent", __name__)

    @ctrl.before_request
    def before_request():
        request.start_time = time()

    @ctrl.route("/agent/ephemeral", methods=["POST"])
    def agent_request():
        """Generate an ephemeral agent: user agent and cloudflare session cookie."""

        ar = EphemeralAgentRequest()
        params = {}
        try:
            params = ar.load(request.args)
        except ValidationError as err:
            return jsonify(err.messages), 400
        params = dotdict(params)

        arp = EphemeralAgentRequestPayload()
        data = {}
        if request.content_type == "application/json":
            pld = request.get_json()
            if pld is not None:
                try:
                    data = arp.load(pld)
                except ValidationError as err:
                    return jsonify(err.messages), 400

        try:
            url = unquote(params.url)
            cookie, ua = cloudscraper.get_cookie_string(url, **data)
        except Exception as err:
            log.error("Couldn't create an ephemeral agent.", error=err)
            return Response(status=500)

        return (
            jsonify(
                {
                    "User-Agent": ua,
                    "cf_clearance": cookie,
                }
            ),
            200,
        )

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
