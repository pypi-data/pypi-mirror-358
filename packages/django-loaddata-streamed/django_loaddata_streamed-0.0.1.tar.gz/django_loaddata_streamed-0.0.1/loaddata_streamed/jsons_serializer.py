from io import StringIO, BytesIO
import json_stream

from django.core.serializers.base import DeserializationError
from django.core.serializers import json as jsonbase_serializer
from django.core.serializers.python import Deserializer as PythonDeserializer

# The standard serializer streams objects already
Serializer = jsonbase_serializer.Serializer


def Deserializer(stream_or_string, **options):
    """Stream-oriented deserialize of a stream or string of JSON data"""
    try:
        if isinstance(stream_or_string, str):
            stream = json_stream.load(StringIO(stream_or_string))
        elif isinstance(stream_or_string, bytes):
            stream = json_stream.load(BytesIO(stream_or_string))
        else:
            stream = json_stream.load(stream_or_string)

        def objects(stream):
            for row in stream:
                ret = json_stream.to_standard_types(row)
                yield ret
        yield from PythonDeserializer(objects(stream), **options)
    except (GeneratorExit, DeserializationError):
        raise
    except Exception as exc:
        raise DeserializationError() from exc
