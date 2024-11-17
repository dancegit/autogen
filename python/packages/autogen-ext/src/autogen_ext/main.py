import modal

app = modal.App()

@app.function()
def hello():
    return "Hello from AutoGen Extension!"

if __name__ == "__main__":
    with app.run():
        print(hello.remote())
