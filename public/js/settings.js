
let c = 0;

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

dom("submit").addEventListener("click", function() {
  let current = sha256(dom("current").value);
  let newPass = sha256(dom("new").value);
  let verify = sha256(dom("verify").value);

  if (newPass == verify && newPass && dom("new").value) {
    fetch("/api/account/change", {
      method: "POST",
      body: JSON.stringify({
        current: current,
        new: newPass
      })
    }).then(response => {
      if (response.status == 200) {
        log("Success! Password has been changed! You will need to log in on any other devices again.");
        response.json().then(json => {
          localStorage.setItem("token", json.token);
          setCookie("token", json.token);
        });
        dom("current").value = "";
      } else if (response.status == 401) {
        log("Your current password is incorrect!");
      } else {
        log("Something went wrong! Try again later.");
      }
    })
  } else {
    log("Your passwords don't match!");
  }
});

dom("delete").addEventListener("click", function() {
  if (confirm("Are you 100% SURE you want to PERMANENTLY DELETE your account?")) {
    let x = prompt("By typing in your password below to confirm your identity, you acknowledge that this action is 100% IRREVERSIBLE.");
    if (x) {
      fetch("/api/account/delete", {
        method: "DELETE",
        body: JSON.stringify({
          passhash: sha256(x)
        })
      }).then(response => {
        if (response.status == 200) {
          window.location.href = "/logout";
        } else if (response.status == 401) {
          log("Wrong password!");
        } else {
          log("Something went wrong! Try again later.")
        }
      });
    }
  }
});
