import React, { useState, useEffect, useCallback } from 'react';
import ReactDOM from 'react-dom';
import ReactFlow, { addEdge, Background, Controls, MiniMap } from 'react-flow-renderer';

const FlowChart = ({ agents, messages }) => {
    const [elements, setElements] = useState([]);

    const onConnect = useCallback((params) => setElements((els) => addEdge(params, els)), []);

    useEffect(() => {
        const nodes = agents.map((agent, index) => ({
            id: agent,
            data: { label: agent },
            position: { x: (index + 1) * 200, y: 20 },
            type: 'default'
        }));

        const edges = messages.map((msg, index) => ({
            id: `e${index}`,
            source: msg.from,
            target: msg.to,
            label: msg.content.substring(0, 20) + (msg.content.length > 20 ? '...' : ''),
            type: 'smoothstep'
        }));

        setElements([...nodes, ...edges]);
    }, [agents, messages]);

    return (
        <ReactFlow
            elements={elements}
            onConnect={onConnect}
            style={{ width: '100%', height: '100%' }}
        >
            <Background />
            <Controls />
            <MiniMap />
        </ReactFlow>
    );
};

document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');
    const form = document.getElementById('taskForm');
    const orchestratorOutput = document.getElementById('orchestratorOutput');
    const agentsOutput = document.getElementById('agentsOutput');
    const graphicalView = document.getElementById('graphicalView');
    let socket;

    const loadedAgentsList = document.getElementById('loadedAgents');
    const activeAgentElement = document.getElementById('activeAgent');

    let agents = ['Orchestrator'];
    let messages = [];

    function updateGraphicalView() {
        ReactDOM.render(
            <FlowChart agents={agents} messages={messages} />,
            graphicalView
        );
    }

    updateGraphicalView();

    function appendMessage(element, message, className = '') {
        console.log(`Appending message: ${message}`);
        const messageElement = document.createElement('div');
        messageElement.className = `agent-message ${className}`;
        messageElement.textContent = message;
        element.appendChild(messageElement);
        element.scrollTop = element.scrollHeight;
    }

    function appendErrorDetails(element, details) {
        console.log(`Appending error details: ${details}`);
        const detailsElement = document.createElement('pre');
        detailsElement.className = 'error-details';
        detailsElement.textContent = details;
        element.appendChild(detailsElement);
        element.scrollTop = element.scrollHeight;
    }

    function updateLoadedAgents(agents) {
        loadedAgentsList.innerHTML = '';
        agents.forEach(agent => {
            const li = document.createElement('li');
            li.textContent = agent;
            loadedAgentsList.appendChild(li);
        });
    }

    function updateActiveAgent(agent) {
        activeAgentElement.textContent = agent;
    }

    if (!form) {
        console.error('taskForm element not found');
        appendMessage(orchestratorOutput, 'Error: Task form not found', 'error');
    } else {
        console.log('Task form found, adding submit event listener');
        form.addEventListener('submit', function(e) {
            console.log('Form submitted');
            e.preventDefault();
            
            // Log all form elements
            console.log('Form elements:', form.elements);
            
            const inputElement = document.getElementById('taskInput');
            console.log('Input element:', inputElement);

            if (!inputElement) {
                throw new Error('Task input element not found');
            }

            const task = inputElement.value.trim();
            console.log('Task value:', task);

            if (!task) {
                throw new Error('Task input is empty');
            }

            console.log('Task to be sent:', task);
        
            orchestratorOutput.innerHTML = '';
            agentsOutput.innerHTML = '';
            appendMessage(orchestratorOutput, 'Processing...', 'status');
            
            console.log(`Connecting to WebSocket: wss://${window.location.host}/ws`);
            socket = new WebSocket(`wss://${window.location.host}/ws`);
            
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
                            messages.push({from: 'Orchestrator', to: 'User', content: data.message});
                            updateGraphicalView();
                            break;
                        case 'error':
                            appendMessage(orchestratorOutput, `Error: ${data.message}`, 'error');
                            if (data.details) {
                                appendErrorDetails(orchestratorOutput, data.details);
                            }
                            break;
                        case 'log':
                            if (data.data.agent === 'Orchestrator') {
                                appendMessage(orchestratorOutput, JSON.stringify(data.data, null, 2));
                            } else {
                                const agentName = data.data.agent || 'Unknown';
                                const message = data.data.message || JSON.stringify(data.data);
                                appendMessage(agentsOutput, `Agent ${agentName}: ${message}`);
                                if (!agents.includes(agentName)) {
                                    agents.push(agentName);
                                }
                                messages.push({from: 'Orchestrator', to: agentName, content: message});
                                updateGraphicalView();
                            }
                            break;
                        case 'agents_loaded':
                            updateLoadedAgents(data.agents);
                            agents = ['Orchestrator', ...data.agents];
                            updateGraphicalView();
                            break;
                        case 'agent_called':
                            updateActiveAgent(data.agent);
                            break;
                        case 'warning':
                            appendMessage(orchestratorOutput, `Warning: ${data.message}`, 'warning');
                            break;
                        case 'retry':
                            appendMessage(orchestratorOutput, `Retry attempt ${data.attempt} of ${data.max_retries}`, 'warning');
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
    }

    // Add a ping function to keep the connection alive
    function ping() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({type: 'ping'}));
        }
    }

    // Set up a timer to ping the server every 30 seconds
    setInterval(ping, 30000);

    console.log('JavaScript initialization complete');

    // Additional debugging: Log the form and input element after a short delay
    setTimeout(() => {
        console.log('Delayed logging:');
        console.log('Form element:', document.getElementById('taskForm'));
        console.log('Input element:', document.getElementById('taskInput'));
        if (document.getElementById('taskInput')) {
            console.log('Input element value:', document.getElementById('taskInput').value);
        } else {
            console.log('Input element not found in delayed logging');
        }
    }, 1000);
});
