CONTENT_DIRECTORY = "./public/"
SAVING_DIRECTORY = "./save/"

UPGRADE_TO_HTTPS = False

import hashlib
import random
import shutil
import flask
import json
import os

from typing import Union, Callable
from flask import request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

app = flask.Flask(__name__)
app.url_map.strict_slashes = False

def validate_color(color: str) -> bool:
    if len(color) != 7 or color[0] != "#":
        return False

    for i in color[1::]:
        if i not in "abcdef0123456789":
            return False

    return True

def sort_list(l: list[list[str]]) -> list[list[str]]:
    output = []
    for i in l:
        if i[0] and i[1] in ["1", "2", "3", "4"]:
            output.append(i)

    return sorted(output, key=lambda x: {"1": "d", "2": "c", "3": "b", "4": "a"}[x[1]] + x[0])

def return_dynamic_content_type(content: Union[str, bytes], content_type: str="text/html") -> flask.Response:
    response = flask.make_response(content)
    response.headers["Content-Type"] = content_type
    return response

def sha(string: Union[str, bytes]) -> str:
    if type(string) == str:
        return hashlib.sha256(str.encode(string)).hexdigest()
    elif type(string) == bytes:
        return hashlib.sha256(string).hexdigest()
    return ""

def ensure_file(path: str, *, default_value: str="", folder: bool=False) -> None:
    if os.path.exists(path):
        if folder and not os.path.isdir(path):
            os.remove(path)
            os.makedirs(path)
        elif not folder and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            f = open(path, "w")
            f.write(default_value)
            f.close()
    else:
        if folder:
            os.makedirs(path)
        else:
            f = open(path, "w")
            f.write(default_value)
            f.close()

def escape_html(string: str) -> str:
    return string.replace("&", "&amp;").replace("<", "&lt;").replace("\"", "&quot;")

def generate_token(username: str, passhash: str) -> str:
    return sha(sha(f"{username}:{passhash}") + "among us in real life, sus, sus")

def list_public(
    sort: str="alphabetical",
    page: int=0,
    limit: int=25
) -> dict:
    # Sort: "alphabetical", "random"
    # Page: for "alphabetical", page for next. 0 is first page, 1 is second...

    x = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())
    output = {
        "end": True,
        "list": []
    }

    if sort == "alphabetical":
        x = x[limit * page::]
        output["end"] = len(x) <= limit
        for i in x[:limit:]:
            q = json.loads(open(f"{SAVING_DIRECTORY}{i}.json", "r").read())
            output["list"].append({
                "colors": q["colors"],
                "display_name": q["display_name"],
                "bio": q["description"],
                "username": i
            })

    elif sort == "random":
        random.shuffle(x)
        for i in x[:limit:]:
            q = json.loads(open(f"{SAVING_DIRECTORY}{i}.json", "r").read())
            output["list"].append({
                "colors": q["colors"],
                "display_name": q["display_name"],
                "bio": q["description"],
                "username": i
            })

    return output

def create_file_serve(file) -> Callable:
    x = lambda property=None: flask.send_file(f"{CONTENT_DIRECTORY}{file}")
    x.__name__ = file
    return x

def create_folder_serve(directory) -> Callable:
    x = lambda file: flask.send_from_directory(f"{CONTENT_DIRECTORY}{directory}", file)
    x.__name__ = directory
    return x

def api_account_login():
    try:
        x = json.loads(request.data)
        username = x["username"].replace(" ", "").lower()
        passhash = x["password"]
    except json.JSONDecodeError:
        flask.abort(400)
    except KeyError:
        flask.abort(400)

    if len(username) > 24 or len(username) < 1:
        flask.abort(400)

    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_-":
            return {
                "valid": False,
                "reason": "User doesn't exist."
            }

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
    except FileNotFoundError:
        return {
            "valid": False,
            "reason": "User doesn't exist."
        }

    token = generate_token(username, passhash)

    try:
        enforced_username = open(f"{SAVING_DIRECTORY}tokens/{token}.txt", "r").read()
    except FileNotFoundError:
        return {
            "valid": False,
            "reason": "Invalid password"
        }

    if enforced_username != username:
        return {
            "valid": False,
            "reason": "Invalid password"
        }

    return {
        "valid": True,
        "token": token
    }

def api_account_signup():
    try:
        x = json.loads(request.data)
        username = x["username"].replace(" ", "").lower()
        passhash = x["password"]
    except json.JSONDecodeError:
        flask.abort(400)
    except KeyError:
        flask.abort(400)

    if len(x["username"]) > 24 or len(username) < 1:
        flask.abort(400)

    if len(passhash) != 64:
        flask.abort(400)

    for i in passhash:
        if i not in "abcdef0123456789":
            flask.abort(400)

    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_-":
            return {
                "valid": False,
                "reason": "Username can only contain a-z, 0-9, underscores, and hyphens."
            }

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
        return {
            "valid": False,
            "reason": "Username taken."
        }
    except FileNotFoundError:
        pass

    token = generate_token(username, passhash)
    ensure_file(f"{SAVING_DIRECTORY}tokens/{token}.txt", default_value=username)
    ensure_file(f"{SAVING_DIRECTORY}{username}.json", default_value=json.dumps({
        "username": username,
        "display_name": x["username"],
        "description": "",
        "colors": {
            "accent": "#ff0000",
            "text": "#ffffff",
            "background": "#111122"
        },
        "names": [
            [x["username"], "4"]
        ],
        "pronouns": [
            ["he/him", "3"],
            ["it/its", "3"],
            ["she/her", "3"],
            ["they/them", "3"]
        ],
        "honorifics": [
            ["ma'am", "3"],
            ["madam", "3"],
            ["mir", "3"],
            ["mr.", "3"],
            ["ms.", "3"],
            ["mx.", "3"],
            ["sai", "3"],
            ["shazam", "3"],
            ["sir", "3"],
            ["zam", "3"]
        ],
        "compliments": [
            ["cute", "3"],
            ["handsome", "3"],
            ["hot", "3"],
            ["pretty", "3"],
            ["sexy", "3"]
        ],
        "relationship": [
            ["beloved", "3"],
            ["boyfriend", "3"],
            ["darling", "3"],
            ["enbyfriend", "3"],
            ["friend", "3"],
            ["girlfriend", "3"],
            ["husband", "3"],
            ["partner", "3"],
            ["wife", "3"]
        ]
    }))

    return return_dynamic_content_type(json.dumps({
        "valid": True,
        "token": token
    }))

def api_account_info_(user):
    try:
        return return_dynamic_content_type(
            open(f"{SAVING_DIRECTORY}{user}.json").read(),
            "application/json"
        )
    except FileNotFoundError:
        flask.abort(404)

def api_account_self():
    try:
        return return_dynamic_content_type(
            open(SAVING_DIRECTORY + open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read() + ".json", 'r').read(),
            "application/json"
        )
    except FileNotFoundError:
        flask.abort(404)

def api_account_change():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    if generate_token(username, x["current"]) != request.cookies["token"]:
        flask.abort(401)

    new = generate_token(username, x["new"])
    os.rename(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', f'{SAVING_DIRECTORY}tokens/{new}.txt')

    return {
        "token": new
    }

def api_account_delete():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    token = generate_token(username, x["passhash"])
    if generate_token(username, x["passhash"]) != request.cookies["token"]:
        flask.abort(401)

    os.remove(f"{SAVING_DIRECTORY}tokens/{token}.txt")
    os.remove(f"{SAVING_DIRECTORY}{username}.json")

    f = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())
    if username in f:
        f.remove(username)
        g = open(f"{SAVING_DIRECTORY}public/list.json", "w")
        g.write(json.dumps(f))
        g.close()

    return "200 OK"

def api_save():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    user_data = json.loads(open(f"{SAVING_DIRECTORY}{username}.json", "r").read())

    if "display_name" in x and len(x["display_name"]) < 64 and len(x["display_name"]) > 0:
        user_data["display_name"] = x["display_name"]

    if "description" in x and len(x["description"]) < 512:
        user_data["description"] = x["description"]

    if "public" in x:
        user_data["public"] = bool(x["public"])
        public_list = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())

        if user_data["public"] and username not in public_list:
            public_list.append(username)
        elif not user_data["public"] and username in public_list:
            public_list.remove(username)

        f = open(f"{SAVING_DIRECTORY}public/list.json", "w")
        f.write(json.dumps(sorted(public_list)))
        f.close()

    if "colors" in x:
        if "accent" in x["colors"] and validate_color(x["colors"]["accent"]):
            user_data["colors"]["accent"] = x["colors"]["accent"]

        if "background" in x["colors"] and validate_color(x["colors"]["background"]):
            user_data["colors"]["background"] = x["colors"]["background"]

        if "text" in x["colors"] and validate_color(x["colors"]["text"]):
            user_data["colors"]["text"] = x["colors"]["text"]

    if "names" in x:
        names = []
        for i in x["names"]:
            if int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                names.append(i)
        user_data["names"] = sort_list(names)

    if "pronouns" in x:
        pronouns = []
        for i in x["pronouns"]:
            if int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                pronouns.append(i)
        user_data["pronouns"] = sort_list(pronouns)

    if "honorifics" in x:
        honorifics = []
        for i in x["honorifics"]:
            if int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                honorifics.append(i)
        user_data["honorifics"] = sort_list(honorifics)

    if "compliments" in x:
        compliments = []
        for i in x["compliments"]:
            if int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                compliments.append(i)
        user_data["compliments"] = sort_list(compliments)

    if "relationship" in x:
        relationship = []
        for i in x["relationship"]:
            if int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                relationship.append(i)
        user_data["relationship"] = sort_list(relationship)

    f = open(f"{SAVING_DIRECTORY}{username}.json", "w")
    f.write(json.dumps(user_data))
    f.close()

    return "200 OK"

def api_browse():
    return list_public(
        request.args.get("sort"), # type: ignore
        int(request.args.get("page")) if "page" in request.args else 0 # type: ignore
    )

def home():
    if "token" not in request.cookies:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    token = request.cookies['token']

    if len(token) != 64:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    for i in token:
        if i not in "abcdef0123456789":
            return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    try:
        username = open(f"{SAVING_DIRECTORY}tokens/{token}.txt", "r").read()
        user_info = json.loads(open(f"{SAVING_DIRECTORY}{username}.json", "r").read())
    except FileNotFoundError:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    x = open(f"{CONTENT_DIRECTORY}home.html", "r").read()
    x = x.replace("{{USERNAME}}", username)
    x = x.replace("{{DISPL_NAME}}", user_info["display_name"])
    x = x.replace("{{PUBLIC}}", "true" if "public" in user_info and user_info["public"] else "false")
    x = x.replace("{{TOTAL}}", str(len(json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read()))))

    return return_dynamic_content_type(x, "text/html")

ensure_file(SAVING_DIRECTORY, folder=True)
ensure_file(f"{SAVING_DIRECTORY}tokens/", folder=True)
ensure_file(f"{SAVING_DIRECTORY}public", folder=True)
ensure_file(f"{SAVING_DIRECTORY}public/list.json", default_value="[]")

app.route("/")(create_file_serve("index.html"))
app.route("/login")(create_file_serve("login.html"))
app.route("/signup")(create_file_serve("signup.html"))
app.route("/logout")(create_file_serve("logout.html"))
app.route("/browse")(create_file_serve("browse.html"))
app.route("/settings")(create_file_serve("settings.html"))

app.route("/editor")(create_file_serve("editor.html"))
app.route("/u/<path:property>")(create_file_serve("user.html"))
app.route("/home")(home)

app.route("/js/<path:file>")(create_folder_serve("js"))
app.route("/css/<path:file>")(create_folder_serve("css"))

app.route("/api/account/login", methods=["POST"])(api_account_login)
app.route("/api/account/signup", methods=["POST"])(api_account_signup)
app.route("/api/account/info/<path:user>", methods=["GET"])(api_account_info_)
app.route("/api/account/self", methods=["GET"])(api_account_self)
app.route("/api/account/change", methods=["POST"])(api_account_change)
app.route("/api/account/delete", methods=["DELETE"])(api_account_delete)
app.route("/api/save", methods=["PATCH"])(api_save)
app.route("/api/browse", methods=["GET"])(api_browse)

app.errorhandler(404)(create_file_serve("404.html"))

if UPGRADE_TO_HTTPS:
    app.wsgi_app = ProxyFix(app.wsgi_app)

    @app.before_request
    def enforce_https():
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
