import io
import json
import tempfile


def create_temp_json_file(data: dict) -> tempfile.NamedTemporaryFile:
    buffer = io.BytesIO()
    buffer.write(json.dumps(data).encode("utf-8"))
    buffer.seek(0)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(buffer.getvalue())
    return temp_file
