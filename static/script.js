// Function to handle the 'Enter' key press event for sending a message
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}



// Function to send the message to the Flask server and handle the response
async function sendMessage() {
    const userInput = document.getElementById('userInput').value.trim();
    if (!userInput) return;

    appendMessage(userInput, 'user');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userInput }),
        });

        const data = await response.json();
        if (data.results) {
            const results = data.results.map(result => JSON.stringify(result, null, 2)).join('\n');
            appendMessage(results, 'bot');
        } else if (data.error) {
            appendMessage('Error: ' + data.error, 'bot');
        }

    } catch (error) {
        console.error('Fetch error:', error);
        appendMessage('An error occurred.', 'bot');
    }

    document.getElementById('userInput').value = '';
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}

function appendMessage(text, sender) {
    const messageContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'message ' + sender;
    messageElement.textContent = text;
    messageContainer.appendChild(messageElement);
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Optionally, you can implement voice recognition here
function startRecognition() {
    // Implement voice recognition functionality
}
