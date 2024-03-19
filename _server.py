CONTENT_DIRECTORY = "./public/"
SAVING_DIRECTORY = "./save/"

UPGRADE_TO_HTTPS = False

import hashlib
import random
import shutil
import flask
import json
import os

from DotIndex import DotIndex
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

def get_template(json, username):
    def add_to_output(starting, json, key, title):
        starting += f'<div class="added" id="{key}"><h2>{title}</h2>'
        for i in json[key]:
            starting += f"""<div {'class="accent"' if i[1] == '4' else 'style="color: var(--text-low-opacity);"' if i[1] == '1' else ''}>{icons[i[1]]} {escape_html(i[0])}</div>"""
        return starting + "</div>"

    json = DotIndex(json)

    icons = {
        "1": '<svg style="fill: var(--text-low-opacity);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 477.2c-38.2 10.9-78.1-11.2-89-49.4l-5.7-20c-3.7-13-10.4-25-19.5-35l-51.3-56.4c-8.9-9.8-8.2-25 1.6-33.9s25-8.2 33.9 1.6l51.3 56.4c14.1 15.5 24.4 34 30.1 54.1l5.7 20c3.6 12.7 16.9 20.1 29.7 16.5s20.1-16.9 16.5-29.7l-5.7-20c-5.7-19.9-14.7-38.7-26.6-55.5-5.2-7.3-5.8-16.9-1.7-24.9s12.3-13 21.3-13H448c8.8 0 16-7.2 16-16 0-6.8-4.3-12.7-10.4-15-7.4-2.8-13-9-14.9-16.7s.1-15.8 5.3-21.7c2.5-2.8 4-6.5 4-10.6 0-7.8-5.6-14.3-13-15.7-8.2-1.6-15.1-7.3-18-15.2s-1.6-16.7 3.6-23.3c2.1-2.7 3.4-6.1 3.4-9.9 0-6.7-4.2-12.6-10.2-14.9-11.5-4.5-17.7-16.9-14.4-28.8.4-1.3.6-2.8.6-4.3 0-8.8-7.2-16-16-16h-97.5c-12.6 0-25 3.7-35.5 10.7l-61.7 41.1c-11 7.4-25.9 4.4-33.3-6.7s-4.4-25.9 6.7-33.3l61.7-41.1c18.4-12.3 40-18.8 62.1-18.8H384c34.7 0 62.9 27.6 64 62 14.6 11.7 24 29.7 24 50 0 4.5-.5 8.8-1.3 13 15.4 11.7 25.3 30.2 25.3 51 0 6.5-1 12.8-2.8 18.7 11.6 11.8 18.8 27.8 18.8 45.5 0 35.3-28.6 64-64 64h-92.3c4.7 10.4 8.7 21.2 11.8 32.2l5.7 20c10.9 38.2-11.2 78.1-49.4 89zM32 384c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32h64c17.7 0 32 14.3 32 32v224c0 17.7-14.3 32-32 32H32z"/></svg>',
        "2": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M100.5 176c-29 0-52.5 23.5-52.5 52.5V320c0 13.3-10.7 24-24 24S0 333.3 0 320v-91.5C0 173 45 128 100.5 128c29.6 0 57.6 13 76.7 35.6l130.2 153.8c10 11.8 24.6 18.6 40.1 18.6 29 0 52.5-23.5 52.5-52.5V192c0-13.3 10.7-24 24-24s24 10.7 24 24v91.5C448 339 403 384 347.5 384c-29.6 0-57.6-13-76.7-35.6L140.6 194.6c-10-11.8-24.6-18.6-40.1-18.6z"/></svg>',
        "3": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 34.8c-38.2-10.9-78.1 11.2-89 49.4l-5.7 20c-3.7 13-10.4 25-19.5 35l-51.3 56.4c-8.9 9.8-8.2 25 1.6 33.9s25 8.2 33.9-1.6l51.3-56.4c14.1-15.5 24.4-34 30.1-54.1l5.7-20c3.6-12.7 16.9-20.1 29.7-16.5s20.1 16.9 16.5 29.7l-5.7 20c-5.7 19.9-14.7 38.7-26.6 55.5-5.2 7.3-5.8 16.9-1.7 24.9s12.3 13 21.3 13H448c8.8 0 16 7.2 16 16 0 6.8-4.3 12.7-10.4 15-7.4 2.8-13 9-14.9 16.7s.1 15.8 5.3 21.7c2.5 2.8 4 6.5 4 10.6 0 7.8-5.6 14.3-13 15.7-8.2 1.6-15.1 7.3-18 15.2s-1.6 16.7 3.6 23.3c2.1 2.7 3.4 6.1 3.4 9.9 0 6.7-4.2 12.6-10.2 14.9-11.5 4.5-17.7 16.9-14.4 28.8.4 1.3.6 2.8.6 4.3 0 8.8-7.2 16-16 16h-97.5c-12.6 0-25-3.7-35.5-10.7l-61.7-41.1c-11-7.4-25.9-4.4-33.3 6.7s-4.4 25.9 6.7 33.3l61.7 41.1c18.4 12.3 40 18.8 62.1 18.8H384c34.7 0 62.9-27.6 64-62 14.6-11.7 24-29.7 24-50 0-4.5-.5-8.8-1.3-13 15.4-11.7 25.3-30.2 25.3-51 0-6.5-1-12.8-2.8-18.7 11.6-11.8 18.8-27.8 18.8-45.5 0-35.3-28.6-64-64-64h-92.3c4.7-10.4 8.7-21.2 11.8-32.2l5.7-20c10.9-38.2-11.2-78.1-49.4-89zM32 192c-17.7 0-32 14.3-32 32v224c0 17.7 14.3 32 32 32h64c17.7 0 32-14.3 32-32V224c0-17.7-14.3-32-32-32H32z"/></svg>',
        "4": '<svg class="accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="m47.6 300.4 180.7 168.7c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9l180.7-168.7c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141-45.6-7.6-92 7.3-124.6 39.9l-12 12-1-12c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"/></svg>'
    }

    styles = f"--background: {json.colors.background}; --background-low-opacity: {json.colors.background}33; --accent: {json.colors.accent}; --accent-low-opacity: {json.colors.accent}66; --text: {json.colors.text}; --text-low-opacity: {json.colors.text}88;" # type: ignore
    title = f"{escape_html(json.display_name)} (@{username})".replace("{{TEMPLATE}}", "HA" * 50) # type: ignore
    embed = f'<meta name="description" content="{json.display_name} on InfoPage"><meta name="author" content="trinkey"><meta property="og:type" content="website"><meta property="og:title" content="{json.display_name} on InfoPage"><meta property="og:description" content="{json.description}"><meta property="og:url" content="https://infopg.web.app/"><meta property="og:site_name" content="infopg.web.app"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{json.display_name} on InfoPage"><meta name="twitter:description" content="{json.description}">' # type: ignore
    inner = f'<div id="container"><h1 id="name">{escape_html(json.display_name)}</h1><div id="description">{escape_html(json.description)}</div><div id="word-container">' # type: ignore

    inner = add_to_output(inner, json, "names", "Names");
    inner = add_to_output(inner, json, "pronouns", "Pronouns");
    inner = add_to_output(inner, json, "honorifics", "Honorifics");
    inner = add_to_output(inner, json, "compliments", "Compliments");
    inner = add_to_output(inner, json, "relationship", "Relationship<br>Descriptions");

    inner += "</div>"

    return title, inner, styles, embed

def get_user_page(user):
    x = open(f"{CONTENT_DIRECTORY}user.html", "r").read()
    try:
        user_json = json.loads(open(f"{SAVING_DIRECTORY}{user}.json", "r").read())
    except FileNotFoundError:
        return x.replace("{{TEMPLATE}}", '<h1>User not found!</h1><a href="/signup">Sign up</a> - <a href="/login">Log in</a>').replace("{{TITLE}}", "User not found - InfoPage")

    title, inner, styles, embed = get_template(user_json, user)

    return x.replace("<body", f'<body style="{styles}"').replace("{{TITLE}}", title).replace("<title", embed + "<title", 1).replace("{{TEMPLATE}}", inner).replace("HA" * 50, "{{TEMPLATE}}")

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
app.route("/u/<path:user>")(get_user_page)
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
