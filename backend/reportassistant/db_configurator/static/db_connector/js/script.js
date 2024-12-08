// static/db_connector/js/script.js
const togglePassword = document.getElementById("togglePassword");
const passwordField = document.getElementById("id_password");

togglePassword.addEventListener("click", function() {
    // Toggle the type attribute
    const type = passwordField.type === "password" ? "text" : "password";
    passwordField.type = type;

    // Toggle the icon
    const icon = togglePassword.querySelector("i");
    if (type === "password") {
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    } else {
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }
});
