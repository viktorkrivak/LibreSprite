from flask import Flask, request, abort, send_file
from subprocess import check_output
from tempfile import NamedTemporaryFile
from io import BytesIO
from shutil import copyfileobj
from contextlib import contextmanager
from json import loads, dumps
from json.decoder import JSONDecodeError
from logging import basicConfig as log_config, DEBUG
from os.path import getsize
from requests_toolbelt import MultipartEncoder


log_config(level=DEBUG)
app = Flask(__name__)

@contextmanager
def prepare_params(export_params):
    with NamedTemporaryFile(suffix=".aseprite") as temp:
        json_data = {}
        if "json" in request.form:
            json_data = loads(request.form["json"])
        params = []
        for item in json_data.get("params", []):
            if isinstance(item, str):
                params.append(f"--{item}")
            else:
                if len(item) != 2:
                    raise Exception()
                k, v = item
                params.append(f"--{k}")
                params.append(str(v))

        f = request.files["upload"]
        f.save(temp.name)
        app.logger.debug(f"Get file {temp.name} with size {getsize(temp.name)}")
        yield ["-b"] + params + [ temp.name ] + export_params


def call_libresprite(args):
    converted_args = ["/opt/libresprite/libresprite"]
    for arg in args:
        if isinstance(arg, str):
            converted_args.append(arg)
        elif hasattr(arg, "name"):
            converted_args.append(arg.name)
        else:
            raise Exception()
    app.logger.info(f"Call libresprite with params: {converted_args}")
    result = check_output(converted_args)
    lines = result.decode().splitlines(keepends=False)
    while lines and  not lines[0].strip().startswith("{"):
        lines = lines[1:]
    try:
        data = loads("".join(lines))
        return data
    except JSONDecodeError:
        app.logger.error(f"Cannot parse: {lines}")
    # app.logger.info(f"Libresprite return {result}")


@app.route('/save-as', methods=['POST'])
def save_as():
    result = {
            "obj": BytesIO(),
            "name": "output.png"
            }
    with NamedTemporaryFile(suffix=".png") as temp:
        with prepare_params(["--save-as", temp]) as params:
            call_libresprite(params)
            data = copyfileobj(temp, result["obj"])
            app.logger.info(f"Libresprite return {data}")
    result["obj"].seek(0)
    return send_file(result["obj"], as_attachment=True, attachment_filename=result["name"])


@app.route('/sheet', methods=['POST'])
def sheet():
    result = {
            "obj": BytesIO(),
            "name": "output.png"
            }
    with NamedTemporaryFile(suffix=".png") as temp:
        with prepare_params(["--sheet", temp]) as params:
            data = call_libresprite( params )
            copyfileobj(temp, result["obj"])
    result["obj"].seek(0)
    multipart = MultipartEncoder(fields={"description": ("data.json", dumps(data), "application/json"), "image": ("result.png", result["obj"], "image/png")})
    return multipart.to_string(), {'Content-Type': multipart.content_type}
    # return send_file(result["obj"], as_attachment=True, attachment_filename=result["name"])
