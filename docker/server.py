from flask import Flask, request, abort, send_file
from subprocess import check_output
from tempfile import NamedTemporaryFile
from io import BytesIO
from shutil import copyfileobj
from contextlib import contextmanager
from json import loads
from logging import getLogger, DEBUG
from os.path import getsize


LOG = getLogger("server")
LOG.setLevel(DEBUG)
app = Flask(__name__)

@contextmanager
def prepare_params():
    with NamedTemporaryFile(suffix=".aseprite") as temp:
        json_data = {}
        if "json" in request.form:
            json_data = loads(request.form["json"])
        params = []
        for item in json_data.get("params", []):
            if isinstance(item, tuple):
                if len(item) != 2:
                    raise Exception()
                k, v = item
                params.append(f"--{k}")
                params.append(str(v))
            else:
                params.append(f"--{item}")

        f = request.files["upload"]
        f.save(temp.name)
        LOG.debug(f"Get file {temp.name} with size {getsize(temp.name)}")
        yield ["-b", temp.name] + params


def call_libresprite(args):
    converted_args = ["/opt/libresprite/libresprite"]
    for arg in args:
        if isinstance(arg, str):
            converted_args.append(arg)
        elif hasattr(arg, "name"):
            converted_args.append(arg.name)
        else:
            raise Exception()
    LOG.info(f"Call libresprite with params: {converted_args}")
    result = check_output(converted_args)
    LOG.info(f"Libresprite return {result}")


@app.route('/save-as', methods=['POST'])
def save_as():
    params = prepare_params()
    result = {
            "obj": BytesIO(),
            "name": "output.png"
            }
    with prepare_params() as params:
        with NamedTemporaryFile(suffix=".png") as temp:
            call_libresprite( params + ["--save-as", temp])
            copyfileobj(temp, result["obj"])
    result["obj"].seek(0)
    return send_file(result["obj"], as_attachment=True, attachment_filename=result["name"])


@app.route('/sheet', methods=['POST'])
def sheet():
    params = prepare_params()
    result = {
            "obj": BytesIO(),
            "name": "output.png"
            }
    with prepare_params() as params:
        with NamedTemporaryFile(suffix=".png") as temp:
            call_libresprite( params + ["--sheet", temp])
            copyfileobj(temp, result["obj"])
    result["obj"].seek(0)
    return send_file(result["obj"], as_attachment=True, attachment_filename=result["name"])
