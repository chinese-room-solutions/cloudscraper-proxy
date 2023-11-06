"""Agent request form."""

from marshmallow import INCLUDE, Schema, fields, validate


class EphemeralAgentRequestParams(Schema):
    """Proxy request form."""

    url = fields.String(required=True)


class BrowserOptionsSchema(Schema):
    browser = fields.String(required=True, validate=validate.OneOf(["firefox", "chrome"]))
    mobile = fields.Bool(allow_none=True)
    desktop = fields.Bool(allow_none=True)
    platform = fields.String(
        allow_none=True,
        validate=validate.OneOf(["linux", "windows", "darwin", "android", "ios"]),
    )
    custom_ua = fields.String(allow_none=True)


class PersistentAgentRequestData(Schema):
    """Persistent agent request payload schema."""

    disableCloudflareV1 = fields.Boolean(
        required=False, allow_none=True, description="Whether to disable Cloudflare v1."
    )
    allow_brotli = fields.Boolean(
        required=False,
        allow_none=True,
        description="Whether to allow Brotli compression.",
    )
    browser = fields.Nested(
        BrowserOptionsSchema,
        required=False,
        allow_none=True,
        description="Dictionary of browser options. See cloudscraper documentation for more details.",
    )
    delay = fields.Integer(
        required=False,
        allow_none=True,
        description="Delay for IUAM challenge. Extracted from IUAM page, not advised to override.",
    )
    interpreter = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["native", "nodejs", "js2py"]),
        description="The javascript interpreter to use.",
    )
    cipherSuite = fields.String(
        required=False, allow_none=True, description="The cipher suite to use."
    )
    ecdhCurve = fields.String(
        required=False, allow_none=True, description="The ecdh curve to use."
    )

    class Meta:
        unknown = INCLUDE


class EphemeralAgentRequestData(Schema):
    """Ephemeral agent request payload schema."""

    allow_brotli = fields.Boolean(
        required=False,
        allow_none=True,
        description="Whether to allow Brotli compression.",
    )
    browser = fields.Nested(
        BrowserOptionsSchema,
        required=False,
        allow_none=True,
        description="Dictionary of browser options. See cloudscraper documentation for more details.",
    )
    delay = fields.Integer(
        required=False,
        allow_none=True,
        description="Delay for IUAM challenge. Extracted from IUAM page, not advised to override.",
    )
    interpreter = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["native", "nodejs", "js2py"]),
        description="The javascript interpreter to use.",
    )

    class Meta:
        unknown = INCLUDE
