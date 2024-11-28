document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('taskForm');
    const orchestratorOutput = document.getElementById('orchestratorOutput');
    const agentsOutput = document.getElementById('agentsOutput');
    let socket;

    function appendMessage(element, message, className = '') {
        const messageElement = document.createElement('div');
        messageElement.className = `agent-message ${className}`;
        messageElement.textContent = message;
        element.appendChild(messageElement);
        element.scrollTop = element.scrollHeight;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const task = document.getElementById('taskInput').value;
        
        orchestratorOutput.innerHTML = '';
        agentsOutput.innerHTML = '';
        appendMessage(orchestratorOutput, 'Processing...', 'status');
        
        socket = new WebSocket(`ws://${window.location.host}/ws`);
        
        socket.onopen = function(e) {
            socket.send(task);
        };
        
        socket.onmessage = function(event) {
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
            }
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                appendMessage(orchestratorOutput, `Connection closed cleanly, code=${event.code} reason=${event.reason}`, 'status');
            } else {
                appendMessage(orchestratorOutput, 'Connection died', 'error');
            }
        };
        
        socket.onerror = function(error) {
            appendMessage(orchestratorOutput, `Error: ${error.message}`, 'error');
        };
    });
});
