from marshmallow import Schema, fields

class ImageUploadSchema(Schema):
    original_filename = fields.Str(required=True)
    status = fields.Str(required=True)
    uploaded_at = fields.DateTime(required=True)
    result_url = fields.Str(allow_none=True)

class ImageListSchema(Schema):
    images = fields.List(fields.Nested(ImageUploadSchema))