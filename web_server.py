from flask import Flask, render_template, request, abort, Response, json, jsonify
from functools import wraps
import threading, os.path
import configparser
import operator
import lit

app = Flask(__name__)
app.config['DEBUG'] = False

config = configparser.ConfigParser()
config.read("configuration/config.ini")
password = config.get("General", "password")
username = config.get("General", "username")
port = config.getint("General", "port")
ai=None
has_fulfillment=False
if config.has_option("Api", "apiai"):
    import apiai
    apiai_token = config.get("Api", "apiai")
    ai = apiai.ApiAI(apiai_token) 
    print("API.AI is enabled!");

if ai is not None and os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/fulfillment.py"):
    import fulfillment
    has_fulfillment = True
    print("API.AI fulfillment enabled!")

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
        res = lit.start(json["effect"], **json["args"])
    else:
        res = lit.start(json["effect"])
    return res

@app.route("/ai_action", methods = ['POST'])
@requires_auth
def ai_action():
    json = request.get_json()
    action = json['result']['action']
    data = json['result']['parameters']
    if action == 'Lights':
        args = {k.lower():data[k] for k in data if k.lower() != "effect" and data[k] != ''}
        if len(args) == 0:
            res = lit.start(data['Effect'])
        else:
            res = lit.start(data['Effect'], **args)
        return jsonify(speech=res['result'], displayText=res['result'])
    elif has_fulfillment:
        result = fulfillment.process(json)
        if result is None:
            abort(404)
        else:
            return jsonify(speech=res['result'], displayText=res['result'])
    else:
        abort(404)

@app.route("/ai_request", methods = ['POST'])
@requires_auth
def ai_request():
    if ai is None:
        return "Unsupported Action"
    api_request = ai.text_request()
    api_request.query = request.get_data()
    #t = threading.Thread(target=api_request.getresponse)
    #t.start()
    response = api_request.getresponse()
    return jsonify(json.loads(response.read())['result']['fulfillment'])

@app.route("/has_ai", methods = ['GET'])
def has_ai():
    if ai is None:
        return "false"
    else:
        return "true"

@app.route("/get_effects.json", methods = ['GET'])
def effects():
    return jsonify(effects=sorted(lit.get_effects(), key=operator.itemgetter('name')))

@app.route("/get_colors.json", methods = ['GET'])
def colors():
    return jsonify(colors=lit.get_colors())

@app.route("/get_ranges.json", methods = ['GET'])
def ranges():
    return jsonify(sections=[k for k in lit.get_sections()], zones=[k for k in lit.get_zones()])

@app.route("/get_speeds.json", methods = ['GET'])
def speeds():
    return jsonify(speeds=lit.get_speeds())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, threaded=True)
