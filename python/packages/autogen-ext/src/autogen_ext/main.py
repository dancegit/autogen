import modal

stub = modal.Stub("autogen-ext")

@stub.function()
def hello():
    return "Hello from AutoGen Extension!"

if __name__ == "__main__":
    with stub.run():
        print(hello.remote())
