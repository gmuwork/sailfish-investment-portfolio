from marshmallow import fields
from marshmallow import schema


class AccountRegistration(schema.Schema):
    first_name = fields.Str(required=True, data_key="first_name")
    last_name = fields.Str(required=True, data_key="last_name")
    email = fields.Str(required=True, data_key="email")
    password = fields.Str(required=True, data_key="password")
