from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))

class UserLoginSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=100))