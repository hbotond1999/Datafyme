function toggleChat() {
    var chatContainer = document.getElementById('chatContainer');
    if (chatContainer.style.display === 'none' || chatContainer.style.display === '') {
        chatContainer.style.display = 'block';
    } else {
        chatContainer.style.display = 'none';
    }
}

function sendMessage(event) {
    event.preventDefault();
    var form = $('#chatForm');
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        success: function (response) {
            var messagesContainer = $('#messagesContainer');
            messagesContainer.append('<div class="message user-message"><strong>You:</strong> ' + response.user_message + '</div>');
            messagesContainer.append('<div class="message reply-message"><strong>System:</strong> ' + response.system_response + '</div>');
            form[0].reset();

            messagesContainer.animate({ scrollTop: messagesContainer.prop("scrollHeight") }, 1000);
        }
    });
    return false;
}

function clearChat() {
    $.ajax({
        type: 'POST',
        url: '{% url "clear_chat" %}',
        data: {
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function (response) {
            location.reload();
        }
    });
}
