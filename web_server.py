from flask import Flask, render_template, request, abort, Response, jsonify
from functools import wraps
import threading
import ConfigParser
import effects as np
app = Flask(__name__)
config = ConfigParser.ConfigParser()
config.read("config.ini")
password = config.get("General", "password")
username = config.get("General", "username")
port = config.getint("General", "port")


def check_auth(un, pw):
    """This function is called to check if a username /
    password combination is valid.
    """
    return un == username and pw == password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Incorrect username or password', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods = ['GET'])
@requires_auth
def hello():
    return render_template('index.html');

@app.route("/command", methods = ['POST'])
@requires_auth
def command():
    json = request.get_json();
    if "args" in json:
        ret, status = np.start(json["effect"], **json["args"])
    else:
        ret, status = np.start(json["effect"])
    return jsonify(result=ret, status=status)

@app.route("/ai", methods = ['POST'])
@requires_auth
def ai():
    json = request.get_json()
    data = json["result"]["parameters"]
    args = {k.lower():np.get_value_from_string(k, data[k]) for k in data if k.lower() != "effect" and data[k] != ''}
    if len(args) == 0:
        ret, status = np.start(data["Effect"])
    else:
        ret, status = np.start(data["Effect"], **args)

@app.route("/get_effects.json", methods = ['GET'])
def effects():
    return jsonify(effects=np.get_effects())

@app.route("/get_colors.json", methods = ['GET'])
def colors():
    return jsonify(colors=np.get_colors())

@app.route("/get_ranges.json", methods = ['GET'])
def ranges():
    return jsonify(ranges=np.get_ranges())

@app.route("/get_speeds.json", methods = ['GET'])
def speeds():
    return jsonify(speeds=np.get_speeds())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = port)
