import modal
from modal import runner
from .aider_modal import app, run_aider

if __name__ == "__main__":
    runner.deploy_app(app)
    print("Aider agent deployed successfully on Modal!")
    print("You can now use the Aider agent in your AutoGen workflows.")
