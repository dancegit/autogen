import modal
from .aider_modal import stub, run_aider

if __name__ == "__main__":
    modal.runner.deploy_stub(stub)
    print("Aider agent deployed successfully on Modal!")
    print("You can now use the Aider agent in your AutoGen workflows.")
