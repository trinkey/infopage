function addToOutput(starting, json, key, title) {
  starting += `<div class="added" id='${key}'><h2>${title}</h2>`;
  for (let i = 0; i < json[key].length; i++) {
    starting += `<div ${
      json[key][i][1] === "4" ? "class='accent'" :
      json[key][i][1] === "1" ? "style='color: var(--text-low-opacity);'" : ""
    }>${icons[json[key][i][1]]} ${escapeHTML(json[key][i][0])}</div>`;
  }
  starting += "</div>";
  return starting;
}

let x2 = window.location.href.split("?")[0].split("/");

fetch("/api/account/info/" + x2[x2.length - 1].toLowerCase(), {
  "method": "GET"
}).then((response) => (response.json()))
  .then((json) => {
    document.body.setAttribute("style", `--background: ${json.colors.background}; --background-low-opacity: ${json.colors.background}33; --accent: ${json.colors.accent}; --accent-low-opacity: ${json.colors.accent}66; --text: ${json.colors.text}; --text-low-opacity: ${json.colors.text}88;`);
    let x = document.createElement("div");
    let inner = `
      <h1 id="name">${escapeHTML(json.display_name)}</h1>
      <div id="description">${escapeHTML(json.description)}</div>
      <div id="word-container">
    `;

    document.title = `${json.display_name} (@${x2[x2.length - 1]})`;

    inner = addToOutput(inner, json, "names", "Names");
    inner = addToOutput(inner, json, "pronouns", "Pronouns");
    inner = addToOutput(inner, json, "honorifics", "Honorifics");
    inner = addToOutput(inner, json, "compliments", "Compliments");
    inner = addToOutput(inner, json, "relationship", "Relationship<br>Descriptions");

    inner += "</div>";

    x.id = "container";
    x.innerHTML = inner;
    document.body.append(x);
  })
  .catch((err) => {
    document.title = "User not found - InfoPage"
    document.body.innerHTML = "<h1>User not found!</h1><a href=\"/signup\">Sign up</a> - <a href=\"/login\">Log in</a>";
  });
