document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');
    const form = document.getElementById('taskForm');
    const orchestratorOutput = document.getElementById('orchestratorOutput');
    const agentsOutput = document.getElementById('agentsOutput');
    let socket;

    function appendMessage(element, message, className = '') {
        console.log(`Appending message: ${message}`);
        const messageElement = document.createElement('div');
        messageElement.className = `agent-message ${className}`;
        messageElement.textContent = message;
        element.appendChild(messageElement);
        element.scrollTop = element.scrollHeight;
    }

    form.addEventListener('submit', function(e) {
        console.log('Form submitted');
        e.preventDefault();
        const task = document.getElementById('taskInput').value;
        
        orchestratorOutput.innerHTML = '';
        agentsOutput.innerHTML = '';
        appendMessage(orchestratorOutput, 'Processing...', 'status');
        
        console.log(`Connecting to WebSocket: ws://${window.location.host}/ws`);
        socket = new WebSocket(`ws://${window.location.host}/ws`);
        
        socket.onopen = function(e) {
            console.log('WebSocket connection established');
            console.log(`Sending task: ${task}`);
            socket.send(task);
        };
        
        socket.onmessage = function(event) {
            console.log("Received message:", event.data);
            try {
                const data = JSON.parse(event.data);
                
                switch(data.type) {
                    case 'status':
                        appendMessage(orchestratorOutput, data.message, 'status');
                        break;
                    case 'final_answer':
                        appendMessage(orchestratorOutput, `Final Answer: ${data.message}`, 'status');
                        break;
                    case 'error':
                        appendMessage(orchestratorOutput, `Error: ${data.message}`, 'error');
                        break;
                    case 'log':
                        if (data.data.agent === 'Orchestrator') {
                            appendMessage(orchestratorOutput, JSON.stringify(data.data, null, 2));
                        } else {
                            appendMessage(agentsOutput, `Agent ${data.data.agent}: ${data.data.message}`);
                        }
                        break;
                    default:
                        console.warn("Unknown message type:", data.type);
                        appendMessage(orchestratorOutput, `Unknown message type: ${data.type}`, 'error');
                }
            } catch (error) {
                console.error("Error parsing message:", error);
                appendMessage(orchestratorOutput, `Error parsing message: ${error.message}`, 'error');
            }
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                appendMessage(orchestratorOutput, `Connection closed cleanly, code=${event.code} reason=${event.reason}`, 'status');
            } else {
                appendMessage(orchestratorOutput, 'Connection died unexpectedly', 'error');
            }
        };
        
        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            appendMessage(orchestratorOutput, `WebSocket error: ${error.message}`, 'error');
        };
    });
});
