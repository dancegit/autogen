import modal
from autogen_ext.agents.aider_modal import app

if __name__ == "__main__":
    stub = modal.Stub("aider-agent")
    stub.function(app.fastapi_app)

    with stub.run():
        print("Aider agent deployed successfully on Modal!")
        print("You can now use the Aider agent in your AutoGen workflows.")
        print("Available endpoints:")
        print("- POST /aider_chat: Send a message to Aider")
        print("- GET /get_files: List files in the workspace")
        print("- GET /get_file_content: Get the content of a specific file")
        print("- POST /update_file: Update the content of a specific file")
