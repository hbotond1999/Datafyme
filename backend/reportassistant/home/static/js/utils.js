function createElementFromString(htmlStr) {
    const div = document.createElement("div")
    div.innerHTML = htmlStr
    return div
}