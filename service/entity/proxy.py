"""Proxy request form."""

from flask_wtf import FlaskForm

# from marshmallow import INCLUDE, Schema, fields
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, ValidationError


# workaround due to inability of flask_wtf to correctly validate agent_id
def validate_agent_id(form, field):
    try:
        int(field.data)
    except ValueError:
        raise ValidationError("Agent ID must be an integer.")


class ProxyRequest(FlaskForm):
    """Proxy request form."""

    agent_id = IntegerField("agent_id", validators=[validate_agent_id])
    dst = StringField("dst", validators=[DataRequired()])
