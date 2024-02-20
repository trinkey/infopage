import hashlib
import shutil
import flask
import json
import os

from flask import request
from typing import Union, Callable

CONTENT_DIRECTORY = "./public/"
SAVING_DIRECTORY = "./save/"

app = flask.Flask(__name__)

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
    return string.replace("&", "&amp;").replace("<", "&lt;").replace("\"", "&quo;")

def create_file_serve(file) -> Callable:
    x = lambda: flask.send_file(f"{CONTENT_DIRECTORY}{file}")
    x.__name__ = file
    return x

def generate_token(username: str, passhash: str) -> str:
    return sha(sha(f"{username}:{passhash}") + "among us in real life, sus, sus")

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
            return return_dynamic_content_type(json.dumps({
                "valid": False,
                "reason": "User doesn't exist."
            }), "application/json")

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
    except FileNotFoundError:
        return return_dynamic_content_type(json.dumps({
            "valid": False,
            "reason": "User doesn't exist."
        }), "application/json")

    token = generate_token(username, passhash)

    try:
        enforced_username = open(f"{SAVING_DIRECTORY}tokens/{token}.txt", "r").read()
    except FileNotFoundError:
        return return_dynamic_content_type(json.dumps({
            "valid": False,
            "reason": "Invalid password"
        }), "application/json")

    if enforced_username != username:
        return return_dynamic_content_type(json.dumps({
            "valid": False,
            "reason": "Invalid password"
        }), "application/json")

    return return_dynamic_content_type(json.dumps({
        "valid": True,
        "token": token
    }), "application/json")

def api_account_signup():
    try:
        x = json.loads(request.data)
        username = x["username"].replace(" ", "")
        passhash = x["password"]
    except json.JSONDecodeError:
        flask.abort(400)
    except KeyError:
        flask.abort(400)

    if len(username) > 24 or len(username) < 1:
        flask.abort(400)

    if len(passhash) != 64:
        flask.abort(400)

    for i in passhash:
        if i not in "abcdef0123456789":
            flask.abort(400)

    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_-":
            return return_dynamic_content_type(json.dumps({
                "valid": False,
                "reason": "Username can only contain a-z, 0-9, underscores, and hyphens."
            }), "application/json")

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
        return return_dynamic_content_type(json.dumps({
            "valid": False,
            "reason": "Username taken."
        }), "application/json")
    except FileNotFoundError:
        pass

    token = generate_token(username, passhash)
    ensure_file(f"{SAVING_DIRECTORY}tokens/{token}.txt", default_value=username)
    ensure_file(f"{SAVING_DIRECTORY}{username}.json", default_value=json.dumps({
        "username": username,
        "display_name": username,
        "description": "",
        "colors": {
            "accent": "#ff0000",
            "text": "#ffffff",
            "background": "#111122"
        },
        "names": [
            [username, "4"]
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
        ], "relationship": [
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

def api_save():
    # TODO - ADD SORTING

    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    user_data = json.loads(open(f"{SAVING_DIRECTORY}{username}.json", "r").read())

    if "display_name" in x and len(x["display_name"]) < 64 and len(x["display_name"]) > 0:
        user_data["display_name"] = x["display_name"]

    if "description" in x and len(x["description"]) < 512:
        user_data["description"] = x["description"]

    if "colors" in x:
        if "accent" in x["colors"]:
            user_data["colors"]["accent"] = x["colors"]["accent"]

        if "background" in x["colors"]:
            user_data["colors"]["background"] = x["colors"]["background"]

        if "text" in x["colors"]:
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

def u_(username):
    return flask.send_file(f"{CONTENT_DIRECTORY}user.html")

# levels:
# 4 - love
# 3 - good
# 2 - okay
# 1 - bad

ensure_file(SAVING_DIRECTORY, folder=True)
ensure_file(f"{SAVING_DIRECTORY}tokens/", folder=True)

app.route("/")(create_file_serve("index.html"))
app.route("/login")(create_file_serve("login.html"))
app.route("/signup")(create_file_serve("signup.html"))
app.route("/logout")(create_file_serve("logout.html"))
app.route("/editor")(create_file_serve("editor.html"))
app.route("/u/<path:username>")(u_)
app.route("/js/<path:file>")(create_folder_serve("js"))
app.route("/css/<path:file>")(create_folder_serve("css"))

app.route("/api/account/login", methods=["POST"])(api_account_login)
app.route("/api/account/signup", methods=["POST"])(api_account_signup)
app.route("/api/account/info/<path:user>", methods=["GET"])(api_account_info_)
app.route("/api/account/self", methods=["GET"])(api_account_self)
app.route("/api/save", methods=["PATCH"])(api_save)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
