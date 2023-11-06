"""Proxy request form."""

from marshmallow import Schema, fields


class ProxyRequestParams(Schema):
    """Proxy request form."""

    agent_id = fields.Integer(required=True)
    dst = fields.String(required=True)
