"""Proxy controller module porovides the proxy blueprint."""

import gzip
from time import time
from urllib.parse import unquote

from flask import Blueprint, Response, jsonify, make_response, request
from structlog import get_logger

from entity.proxy import ProxyRequest
from utils.agent_pool import AgentPool


def construct_proxy_blueprint(agent_pool: AgentPool):
    """Construct the proxy blueprint."""

    log = get_logger(__name__)
    ctrl = Blueprint("proxy", __name__)

    @ctrl.before_request
    def before_request():
        request.start_time = time()

    @ctrl.route("/proxy", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    def proxy_request():
        """Wrap the request with cloudscraper and proxy to the destination."""

        pr = ProxyRequest(request.args)
        if not pr.validate():
            return jsonify(pr.errors), 400

        agent_id = pr.agent_id.data
        url = unquote(pr.dst.data)
        if agent_id in agent_pool:
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
            return flask_response
        else:
            return Response(status=404)

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


def filter_headers(headers: dict[str, str]) -> dict[str, str]:
    """Filter out headers that are not allowed to be proxied."""

    headers.pop("Accept", None)
    headers.pop("Accept-Encoding", None)
    headers.pop("Accept-Language", None)
    headers.pop("Connection", None)
    headers.pop("Content-Length", None)
    headers.pop("Host", None)
    headers.pop("User-Agent", None)

    return headers
