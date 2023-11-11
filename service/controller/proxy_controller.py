"""Proxy controller module provides the proxy blueprint."""

import gzip
from random import choice
from time import time
from urllib.parse import unquote

from entity.proxy import ProxyRequestParams
from flask import make_response, request
from flask_smorest import Blueprint
from structlog import get_logger
from utils.agent_pool import AgentPool
from utils.dotdict import dotdict


def construct_proxy_blueprint(
    agent_pool: AgentPool, proxy_configs: list[dict] = [{}]
) -> Blueprint:
    """Construct the proxy blueprint."""

    log = get_logger(__name__)
    bp = Blueprint("proxy", __name__, url_prefix="/proxy", description="Proxy API.")

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

    @bp.route("", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    @bp.arguments(ProxyRequestParams, location="query")
    def proxy(params):
        """Proxy the request as it is. Returns the response from the destination server. agent_id from request parameters is in precedence over the one from cookies."""

        params = dotdict(params)
        url = unquote(params.dst)
        agent_id = params.agent_id
        if agent_id is None:
            agent_id = request.cookies.get("agent_id")
            if agent_id is not None:
                agent_id = int(agent_id)
        if agent_id is None or agent_id not in agent_pool:
            agent_id, _ = agent_pool.generate(**choice(proxy_configs))

        response = agent_pool[agent_id].request(
            request.method,
            url,
            headers=filter_headers(dict(request.headers)),
            data=request.data,
            cookies=request.cookies,
        )

        # Decode chunked response
        if "chunked" in response.headers.get("Transfer-Encoding", ""):
            content = b"".join(response.iter_content(8192))
        else:
            content = response.content

        # Decompress gzip content
        if response.headers.get("Content-Encoding") == "gzip":
            if content[:2] == b"\x1f\x8b":  # Check for gzip magic numbers
                content = gzip.decompress(content)

        # Convert requests.Response to Flask response
        flask_response = make_response(content, response.status_code)
        for name, value in response.headers.items():
            if name not in {"Content-Encoding", "Transfer-Encoding"}:
                flask_response.headers[name] = value
        flask_response.set_cookie("agent_id", str(agent_id))

        return flask_response

    return bp


def filter_headers(headers: dict[str, str]) -> dict[str, str]:
    """Filter out headers that are not allowed to be proxied."""

    disallowed_headers = [
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Connection",
        "Content-Length",
        "Host",
        "User-Agent",
    ]
    for header in disallowed_headers:
        headers.pop(header, None)

    return headers
