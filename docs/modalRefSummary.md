# Modal Reference Summary

This document provides a concise overview of the most important Modal functionality for programmers.

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

## Key Classes and Methods

### modal.App

- `modal.App()`: Create a new Modal application.
  ```python
  app = modal.App()
  ```

- `@app.function()`: Decorator to register a function with the app.
  ```python
  @app.function()
  def my_function():
      pass
  ```

- `@app.cls()`: Decorator to register a class with the app.
  ```python
  @app.cls()
  class MyClass:
      def __init__(self):
          pass
  ```

- `app.run()`: Context manager to run the app.
  ```python
  with app.run():
      result = my_function.remote()
  ```

### modal.Function

- `@app.function()`: Main decorator for creating Modal functions.
  ```python
  @app.function()
  def process_data(data):
      return data.upper()
  ```

- `function.remote()`: Call the function remotely.
  ```python
  result = process_data.remote("hello")
  ```

- `function.map()`: Parallel map over inputs.
  ```python
  results = process_data.map(["hello", "world", "modal"])
  ```

### modal.Image

- `modal.Image.debian_slim()`: Create a base Debian image.
  ```python
  image = modal.Image.debian_slim()
  ```

- `image.pip_install()`: Install Python packages.
  ```python
  image = modal.Image.debian_slim().pip_install("numpy", "pandas")
  ```

- `image.apt_install()`: Install system packages.
  ```python
  image = modal.Image.debian_slim().apt_install("ffmpeg")
  ```

- `image.dockerfile_commands()`: Run custom Dockerfile commands.
  ```python
  image = modal.Image.debian_slim().dockerfile_commands("RUN echo 'custom command'")
  ```

### modal.Mount

- `modal.Mount.from_local_dir()`: Create a mount from a local directory.
  ```python
  mount = modal.Mount.from_local_dir("./data")
  ```

- `modal.Mount.from_local_file()`: Create a mount from a local file.
  ```python
  mount = modal.Mount.from_local_file("./config.json")
  ```

### modal.Secret

- `modal.Secret.from_name()`: Reference a secret by name.
  ```python
  secret = modal.Secret.from_name("my-api-key")
  ```

- `modal.Secret.from_dict()`: Create a secret from a dictionary.
  ```python
  secret = modal.Secret.from_dict({"API_KEY": "your-api-key-here"})
  ```

### modal.Volume

- `modal.Volume.from_name()`: Reference a volume by name.
  ```python
  volume = modal.Volume.from_name("my-persistent-data")
  ```

- `volume.commit()`: Persist changes to the volume.
  ```python
  @app.function(volumes={"/data": volume})
  def update_data():
      with open("/data/file.txt", "w") as f:
          f.write("New data")
      volume.commit()
  ```

- `volume.reload()`: Fetch latest changes from the volume.
  ```python
  @app.function(volumes={"/data": volume})
  def read_data():
      volume.reload()
      with open("/data/file.txt", "r") as f:
          return f.read()
  ```

## Important Decorators

- `@modal.web_endpoint()`: Create a web endpoint.
  ```python
  @app.function()
  @modal.web_endpoint(method="GET")
  def hello_web(name: str = "World"):
      return f"Hello, {name}!"
  ```

- `@modal.asgi_app()`: Register an ASGI app.
  ```python
  from fastapi import FastAPI

  fastapi_app = FastAPI()

  @app.function()
  @modal.asgi_app()
  def fastapi_function():
      return fastapi_app
  ```

- `@modal.wsgi_app()`: Register a WSGI app.
  ```python
  from flask import Flask

  flask_app = Flask(__name__)

  @app.function()
  @modal.wsgi_app()
  def flask_function():
      return flask_app
  ```

- `@modal.enter()`: Lifecycle method for container startup.
  ```python
  @app.cls()
  class MyClass:
      @modal.enter()
      def initialize(self):
          print("Container starting up")
  ```

- `@modal.exit()`: Lifecycle method for container shutdown.
  ```python
  @app.cls()
  class MyClass:
      @modal.exit()
      def cleanup(self):
          print("Container shutting down")
  ```

- `@modal.build()`: Method to execute during image build.
  ```python
  @app.cls()
  class MyClass:
      @modal.build()
      def build_step(self):
          print("This runs during image build")
  ```

## Utility Functions

- `modal.forward()`: Expose a port from a container.
  ```python
  @app.function()
  def run_server():
      import http.server
      with modal.forward(8000):
          http.server.HTTPServer(("", 8000), http.server.SimpleHTTPRequestHandler).serve_forever()
  ```

- `modal.interact()`: Enable interactive input in a container.
  ```python
  @app.function()
  def interactive_function():
      modal.interact()
      name = input("Enter your name: ")
      print(f"Hello, {name}!")
  ```

- `modal.is_local()`: Check if code is running locally or in Modal.
  ```python
  @app.function()
  def check_environment():
      if modal.is_local():
          print("Running locally")
      else:
          print("Running in Modal cloud")
  ```

## Scheduling and Retries

- `modal.Period()`: Schedule functions to run periodically.
  ```python
  @app.function(schedule=modal.Period(hours=1))
  def hourly_task():
      print("This runs every hour")
  ```

- `modal.Cron()`: Schedule functions using cron syntax.
  ```python
  @app.function(schedule=modal.Cron("0 9 * * *"))
  def daily_at_9am():
      print("This runs every day at 9:00 AM")
  ```

- `modal.Retries()`: Configure retry policies for functions.
  ```python
  @app.function(retries=modal.Retries(max_retries=3, backoff_coefficient=2))
  def retry_function():
      # This function will retry up to 3 times with exponential backoff
      pass
  ```

## GPU Support

- `gpu="T4"`, `gpu="A100"`, etc.: Request specific GPU types.
  ```python
  @app.function(gpu="T4")
  def gpu_function():
      import torch
      print(f"Using GPU: {torch.cuda.get_device_name(0)}")
  ```

- `modal.gpu.GPU()`: Configure custom GPU requirements.
  ```python
  @app.function(gpu=modal.gpu.A100(count=2))
  def multi_gpu_function():
      import torch
      print(f"Number of GPUs: {torch.cuda.device_count()}")
  ```

## Best Practices

1. Use `modal.Image` to create reproducible environments.
2. Leverage `modal.Mount` for including local files and directories.
3. Utilize `modal.Secret` for managing sensitive information.
4. Use `modal.Volume` for persistent storage between function calls.
5. Implement proper error handling and retries for robustness.
6. Take advantage of GPU acceleration when needed.
7. Use web endpoints for creating serverless APIs and applications.

Remember to consult the full Modal documentation for detailed information on these features and more advanced usage scenarios.
