document.getElementById("submitButton").addEventListener('click', () => {
    const form = document.getElementById("databaseForm");
    const formData = new FormData(form);

    // Töröljük az előző hibajelzéseket
    document.querySelectorAll(".error-message").forEach(el => el.remove());
    document.querySelectorAll(".is-invalid").forEach(el => el.classList.remove("is-invalid"));

    fetch("add_connection", {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken') // Django CSRF token
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Validation failed');
        }
    })
    .then(data => {
        if (data.success) {
            document.getElementById('openAddDatabaseModal').click();
            location.reload()
        } else {
            const errors = JSON.parse(data.errors);

            // Hibák megjelenítése
            for (const [field, errorList] of Object.entries(errors)) {
                const inputElement = form.querySelector(`[name="${field}"]`);
                if (inputElement) {

                    inputElement.classList.add("is-invalid");

                    const errorMessage = document.createElement("div");
                    errorMessage.className = "invalid-feedback error-message";
                    errorMessage.textContent = errorList.map(error => error.message).join(", ");
                    inputElement.parentElement.appendChild(errorMessage);
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred.');
    });
});
