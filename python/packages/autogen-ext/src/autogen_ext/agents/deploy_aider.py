import modal
from autogen_ext.agents.aider_modal import app as fastapi_app

if __name__ == "__main__":
    modal_app = modal.App("aider-agent")
    @modal_app.function()
    def fastapi_endpoint():
        return fastapi_app

    with modal_app.run():
        print("Aider agent deployed successfully on Modal!")
        print("You can now use the Aider agent in your AutoGen workflows.")
        print("Available endpoints:")
        print("- POST /aider_chat: Send a message to Aider")
        print("- GET /get_files: List files in the workspace")
        print("- GET /get_file_content: Get the content of a specific file")
        print("- POST /update_file: Update the content of a specific file")
