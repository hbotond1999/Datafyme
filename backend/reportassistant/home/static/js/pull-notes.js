function fetchNotifications(url, csrf_token) {

    const toastContainer = document.getElementById('toastContainer');
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrf_token
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        data.forEach(note => {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.role = 'alert';
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            toast.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">${note.level}</strong>
                    <small>${new Date(note.created).toLocaleTimeString()}</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${note.text}
                </div>
            `;
            toastContainer.appendChild(toast);

            // Show the toast
            const bootstrapToast = new bootstrap.Toast(toast);
            bootstrapToast.show();

            // Set a timeout to hide and remove the toast after 10 seconds
            setTimeout(() => {
                bootstrapToast.hide();
            }, 10000);

            // Remove the toast element after it hides
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        });
    })
    .catch(error => {
        console.error('Error fetching notifications:', error);
    });
}
