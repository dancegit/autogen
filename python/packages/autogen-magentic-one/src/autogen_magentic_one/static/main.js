document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('taskForm');
    const output = document.getElementById('output');
    let socket;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const task = document.getElementById('task').value;
        
        output.innerHTML = '';
        
        socket = new WebSocket(`ws://${window.location.host}/ws`);
        
        socket.onopen = function(e) {
            socket.send(task);
        };
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'status':
                case 'final_answer':
                case 'error':
                    output.innerHTML += `<p><strong>${data.type}:</strong> ${data.message}</p>`;
                    break;
                case 'log':
                    output.innerHTML += `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    break;
            }
            
            output.scrollTop = output.scrollHeight;
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.log('[close] Connection died');
            }
        };
        
        socket.onerror = function(error) {
            console.log(`[error] ${error.message}`);
        };
    });
});
