"""Proxy request form."""

from marshmallow import Schema, fields


class ProxyRequest(Schema):
    """Proxy request form."""

    agent_id = fields.Integer(required=True)
    dst = fields.String(required=True)
