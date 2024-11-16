# Modal Reference Summary

This document provides a comprehensive overview of Modal functionality for programmers, including deployment, environment variables, managing deployments, building agents, security, scaling, and deploying Docker containers.

## Core Concepts

1. **App**: The main container for Modal applications.
   ```python
   import modal

   app = modal.App()
   ```

2. **Function**: Serverless functions that run in the cloud.
   ```python
   @app.function()
   def hello(name):
       return f"Hello, {name}!"
   ```

3. **Image**: Container images for running functions.
   ```python
   image = modal.Image.debian_slim().pip_install("numpy")
   ```

4. **Mount**: Mechanism to include local files in cloud environments.
   ```python
   mount = modal.Mount.from_local_dir("./data")
   ```

5. **Secret**: Secure storage for sensitive information.
   ```python
   secret = modal.Secret.from_name("my-api-key")
   ```

6. **Volume**: Persistent storage accessible across function calls.
   ```python
   volume = modal.Volume.from_name("my-volume")
   ```




## Deployment

### Creating and Managing Deployments

1. Deploy an app using the CLI:
   ```bash
   modal deploy my_app.py
   ```

2. Deploy programmatically:
   ```python
   from modal import deploy_app

   deploy_app(app, name="my-app")
   ```

3. View deployments:
   ```bash
   modal app list
   ```

4. Stop a deployment:
   ```bash
   modal app stop my-app
   ```

5. Rollback to a previous version:
   ```bash
   modal app rollback my-app v3
   ```

### Environment Variables

1. Set environment variables in the Modal dashboard or using secrets:
   ```python
   secret = modal.Secret.from_name("my-env-vars")

   @app.function(secrets=[secret])
   def my_function():
       import os
       print(os.environ["MY_ENV_VAR"])
   ```

2. Access runtime environment variables:
   ```python
   @app.function()
   def get_env_info():
       import os
       print(f"Cloud Provider: {os.environ['MODAL_CLOUD_PROVIDER']}")
       print(f"Region: {os.environ['MODAL_REGION']}")
   ```

## Security

Modal prioritizes security in its serverless infrastructure:

1. **Sandboxed Execution**: Functions run in isolated containers, preventing interference between different workloads.

2. **Secrets Management**: Use `modal.Secret` to securely store and access sensitive information:
   ```python
   secret = modal.Secret.from_name("my-api-key")

   @app.function(secrets=[secret])
   def secure_function():
       # Access the secret securely
       pass
   ```

3. **HTTPS by Default**: All Modal endpoints use HTTPS, ensuring encrypted communication.

4. **Access Controls**: Implement fine-grained access controls for your Modal resources using the dashboard.

5. **Audit Logging**: Modal provides comprehensive logs for monitoring and auditing purposes.

## Scaling

Modal automatically scales your applications based on demand:

1. **Auto-scaling**: Functions automatically scale up or down based on incoming requests.

2. **Concurrent Execution**: Control concurrency with the `concurrency_limit` parameter:
   ```python
   @app.function(concurrency_limit=10)
   def limited_concurrency_function():
       pass
   ```

3. **Batch Processing**: Use `Function.map()` for efficient parallel processing:
   ```python
   results = my_function.map(input_list)
   ```

4. **GPU Scaling**: Easily scale GPU-accelerated workloads:
   ```python
   @app.function(gpu="T4")
   def gpu_function():
       pass
   ```

## Deploying Docker Containers

While Modal primarily uses its own container system, you can integrate Docker containers:

1. **Using Docker Images**: Import existing Docker images into Modal:
   ```python
   image = modal.Image.from_registry("your-docker-image:tag")

   @app.function(image=image)
   def docker_based_function():
       pass
   ```

2. **Dockerfile Integration**: Use a Dockerfile to define your Modal image:
   ```python
   image = modal.Image.from_dockerfile("./Dockerfile")
   ```

3. **Docker Compose**: For complex setups, consider using Modal's multi-container support to replicate Docker Compose functionality.

## Building Agents

Modal can be used to build complex AI agents using libraries like LangChain or LangGraph. Here's an example of creating a coding agent:

```python
import modal
from langgraph.graph import StateGraph
from langchain.chat_models import ChatOpenAI

app = modal.App()
stub = modal.Stub()

@app.function(
    image=modal.Image.debian_slim().pip_install("langchain", "langgraph"),
    secrets=[modal.Secret.from_name("openai-api-key")]
)
def create_agent():
    llm = ChatOpenAI()

    def generate_code(state):
        human_input = state["human_input"]
        response = llm.predict(f"Write Python code for: {human_input}")
        return {"code": response}

    def execute_code(state):
        code = state["code"]
        try:
            exec(code)
            return {"result": "Code executed successfully"}
        except Exception as e:
            return {"result": f"Error: {str(e)}"}

    workflow = StateGraph()
    workflow.add_node("generate", generate_code)
    workflow.add_node("execute", execute_code)
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "execute")

    return workflow.compile()

@app.local_entrypoint()
def main(task: str):
    agent = create_agent.remote()
    result = agent.invoke({"human_input": task})
    print(result)

# Run with: modal run agent.py --task "Create a function that calculates the factorial of a number"
```



## Advanced Features

### Scheduling and Cron Jobs

```python
@app.function(schedule=modal.Period(days=1))
def daily_task():
    print("This runs every day")

@app.function(schedule=modal.Cron("0 9 * * *"))
def weekday_morning_task():
    print("This runs every weekday at 9:00 AM")
```

### GPU Support

```python
@app.function(gpu="T4")
def gpu_task():
    import torch
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
```

### Web Endpoints

```python
@app.function()
@modal.web_endpoint(method="GET")
def hello_web(name: str = "World"):
    return f"Hello, {name}!"
```

### Asynchronous Programming

```python
@app.function()
async def async_task():
    await asyncio.sleep(1)
    return "Task completed"
```

## Best Practices

1. Use `modal.Image` to create reproducible environments.
2. Leverage `modal.Mount` for including local files and directories.
3. Utilize `modal.Secret` for managing sensitive information.
4. Use `modal.Volume` for persistent storage between function calls.
5. Implement proper error handling and retries for robustness.
6. Take advantage of GPU acceleration when needed.
7. Use web endpoints for creating serverless APIs and applications.
8. Monitor your deployments using the Modal dashboard or CLI.
9. Use environment variables for configuration that may change between deployments.
10. Leverage Modal's scheduling capabilities for recurring tasks.
11. Regularly update your Modal client to benefit from the latest security features.
12. Use Modal's built-in scaling features instead of managing scaling manually.
13. Leverage Modal's container system for most use cases, falling back to Docker integration when necessary.

Remember to consult the full Modal documentation for detailed information on these features and more advanced usage scenarios.
