let darkModeEnabled = (document.cookie.includes("darkMode=true"));

function applyDarkMode() {
    linkElement = document.createElement("link");
    linkElement.setAttribute("rel", "stylesheet");
    linkElement.setAttribute("href", "/static/dark.css");
    linkElement.setAttribute("id", "darkModeStylesheet")
    document.head.appendChild(linkElement);
}

function toggleDarkMode() {
    if (darkModeEnabled) {
        document.cookie = "darkMode=false";
        document.getElementById("darkModeToggle").innerText = "Dark";
        document.getElementById("darkModeStylesheet").remove();
    } else {
        document.getElementById("darkModeToggle").innerText = "Light";
        document.cookie = "darkMode=true";
        applyDarkMode();
    }
    darkModeEnabled = !darkModeEnabled;
}

if (darkModeEnabled) {
    applyDarkMode();
}
