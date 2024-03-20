function log(str) {
  c++;
  document.getElementById("log").innerText = str;
  setTimeout(
    function() {
      --c;
      if (!c) {
        document.getElementById("log").innerText = " ";
      }
    }, 3000
  );
}

function addToOutput(starting, json, key, title) {
  starting += `<div class="added" style="text-align: center;"><div style="text-align: left; margin-bottom: 10px;" id='${key}'><h2>${title}</h2>`; // Title

  for (let i = 0; i < json[key].length; i++) {
    starting += `
    <div id="${key}-${i}" data-id="${i}">
      <select data-select2>
        <option value="4"${json[key][i][1] == 4 ?" selected" : ""}>great</option>
        <option value="3"${json[key][i][1] == 3 ?" selected" : ""}>good</option>
        <option value="2"${json[key][i][1] == 2 ?" selected" : ""}>fine</option>
        <option value="1"${json[key][i][1] == 1 ?" selected" : ""}>bad</option>
      </select>

      <input value="${escapeHTML(json[key][i][0], true)}" maxlength="48">
      <svg onclick="dom('${key}-${i}').remove()">${icons.x}</svg>
    </div>`;
  }
  starting += `</div><button onclick="add_input('${key}');">Add</button></div>`;
  return starting;
}

function add_input(key) {
  let x = document.createElement("div")

  let q = [...document.querySelectorAll(`#${key} div[id^="${key}-"]`)];
  let i = Number(q[q.length - 1] ? q[q.length - 1].dataset.id : "-1") + 1;

  x.id = `${key}-${i}`;
  x.setAttribute("data-id", i);
  x.innerHTML = `
  <select data-select2>
    <option value="4">great</option>
    <option value="3" selected>good</option>
    <option value="2">fine</option>
    <option value="1">bad</option>
  </select>

  <input maxlength="48">
  <svg onclick="dom('${x.id}').remove()">${icons.x}</svg>`;

  dom(key).append(x);
}

function updateColors() {
  document.body.setAttribute("style", `--primary: ${colors.text}; --secondary-low-opacity: ${colors.text}22; --background: ${colors.background}; --background-low-opacity: ${colors.background}33; --accent: ${colors.accent}; --accent-low-opacity: ${colors.accent}66; --text: ${colors.text}; --text-low-opacity: ${colors.text}88;`);
}

function get_list(key) {
  let output = [];
  [...document.querySelectorAll(`#${key} div[id^="${key}-"]`)].forEach((val, index) => {
    output.push([val.querySelector("input").value, val.querySelector("select").value]);
  });
  return output;
}

if (localStorage.getItem("token")) {
  setCookie("token", localStorage.getItem("token"));
} else {
  window.location.href = "/logout";
}

let colors, c;

fetch("/api/account/self", {
  "method": "GET"
}).then((response) => (response.json()))
  .then((json) => {
    colors = json.colors;
    updateColors();

    let x = document.createElement("div");
    let inner = `
      <h2><input maxlength="64" placeholder="Display name..." id="input-display-name" value="${escapeHTML(json.display_name, true)}"></h2>
      <div><textarea maxlength="512" placeholder="About me..." id="input-description">${escapeHTML(json.description)}</textarea></div>
      <div>Text color: <input id="input-col-text" type="color" value="${colors.text}"></div>
      <div>Background color: <input id="input-col-background" type="color" value="${colors.background}"></div>
      <div>Accent color: <input id="input-col-accent" type="color" value="${colors.accent}"></div>
      <div>Public: <input id="public" type="checkbox" ${json.public ? "checked" : ""}></div><br>
      <a href="/home"><button>Home</button></a>
      <a target="_blank" href="/u/${json.username}"><button>Preview</button></a>
      <button onclick="navigator.clipboard.writeText('https://infopg.web.app/u/${json.username}'); log('Copied!');">Share</button>
      <button id="save">Save</button><div id="log"> </div>
      <div id="word-container">
    `;

    inner = addToOutput(inner, json, "names", "Names");
    inner = addToOutput(inner, json, "pronouns", "Pronouns");
    inner = addToOutput(inner, json, "honorifics", "Honorifics");
    inner = addToOutput(inner, json, "compliments", "Compliments");
    inner = addToOutput(inner, json, "relationship", "Relationship<br>Descriptions");

    inner += "</div>";

    x.id = "container";
    x.innerHTML = inner;
    document.body.append(x);

    dom("input-description").addEventListener("input", function() {
      let cursorPosition = this.selectionStart;
      if (this.value.indexOf("\n") !== -1) {
        --cursorPosition;
      }
      this.value = this.value.replaceAll("\n", "").replaceAll("\r", "");
      this.setSelectionRange(cursorPosition, cursorPosition);
    });

    dom("save").addEventListener("click", function() {
      fetch("/api/save", {
        "method": "PATCH",
        "body": JSON.stringify({
          colors: colors,
          display_name: dom("input-display-name").value,
          description: dom("input-description").value,
          names: get_list("names"),
          pronouns: get_list("pronouns"),
          honorifics: get_list("honorifics"),
          compliments: get_list("compliments"),
          relationship: get_list("relationship"),
          public: dom("public").checked
        })
      }).then((response) => (response.text()))
        .then((text) => {
          if (text === "200 OK") {
            log("Saved!");
          } else {
            log("Something went wrong when saving!");
          }
        })
        .catch((err) => {
          log("Something went wrong when saving!");
        })
    });

    dom("input-col-text").addEventListener("input", function() {
      colors.text = this.value;
      updateColors();
    });

    dom("input-col-accent").addEventListener("input", function() {
      colors.accent = this.value;
      updateColors();
    });

    dom("input-col-background").addEventListener("input", function() {
      colors.background = this.value;
      updateColors();
    });
  })
  .catch((err) => {
    window.location.href = "/logout";
  });
