import zlib
from django.db import models

class CompressedTextField(models.BinaryField):
    def _check_str_default_value(self):
        return []

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return zlib.decompress(value).decode()

    def to_python(self, value):
        if isinstance(value, bytes):
            return zlib.decompress(value).decode()
        return value

    def get_prep_value(self, value):
        if isinstance(value, str):
            return zlib.compress(value.encode())


try:
    from jsonfield.fields import JSONFieldMixin
except ImportError:
    pass
else:
    class CompressedJSONField (JSONFieldMixin, models.BinaryField):
        def _check_str_default_value(self):
            return []

        def from_db_value(self, value, expression, connection):
            if value is None:
                return value
            return super().from_db_value(zlib.decompress(value).decode(), expression, connection)

        def to_python(self, value):
            if isinstance(value, bytes):
                return super().to_python(zlib.decompress(value).decode())
            return super().to_python(value)

        def get_prep_value(self, value):
            return zlib.compress(super().get_prep_value(value).encode())