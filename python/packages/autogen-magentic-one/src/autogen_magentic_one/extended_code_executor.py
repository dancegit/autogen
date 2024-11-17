from autogen_core.components.code_executor import CodeExecutor, CodeBlock
import subprocess
import os

class ExtendedCodeExecutor(CodeExecutor):
    async def execute_code_blocks(self, code_blocks, cancellation_token=None):
        results = []
        for block in code_blocks:
            if block.language == "python":
                result = self._execute_python(block.code)
            elif block.language == "javascript":
                result = self._execute_javascript(block.code)
            elif block.language == "java":
                result = self._execute_java(block.code)
            elif block.language == "cpp":
                result = self._execute_cpp(block.code)
            elif block.language == "ruby":
                result = self._execute_ruby(block.code)
            elif block.language == "go":
                result = self._execute_go(block.code)
            elif block.language in ["shell", "sh", "bash"]:
                result = self._execute_shell(block.code)
            elif block.language == "groovy":
                result = self._execute_groovy(block.code)
            elif block.language == "kotlin":
                result = self._execute_kotlin(block.code)
            elif block.language == "scala":
                result = self._execute_scala(block.code)
            else:
                result = f"Unsupported language: {block.language}"
            results.append(result)
        return "\n".join(results)

    def _execute_python(self, code):
        return subprocess.run(["python", "-c", code], capture_output=True, text=True).stdout

    def _execute_javascript(self, code):
        return subprocess.run(["node", "-e", code], capture_output=True, text=True).stdout

    def _execute_java(self, code):
        # This is a simplified version. In practice, you'd need to handle class names, etc.
        with open("Temp.java", "w") as f:
            f.write(code)
        subprocess.run(["javac", "Temp.java"], check=True)
        result = subprocess.run(["java", "Temp"], capture_output=True, text=True).stdout
        os.remove("Temp.java")
        os.remove("Temp.class")
        return result

    def _execute_cpp(self, code):
        with open("temp.cpp", "w") as f:
            f.write(code)
        subprocess.run(["g++", "temp.cpp", "-o", "temp"], check=True)
        result = subprocess.run(["./temp"], capture_output=True, text=True).stdout
        os.remove("temp.cpp")
        os.remove("temp")
        return result

    def _execute_ruby(self, code):
        return subprocess.run(["ruby", "-e", code], capture_output=True, text=True).stdout

    def _execute_go(self, code):
        with open("temp.go", "w") as f:
            f.write(code)
        result = subprocess.run(["go", "run", "temp.go"], capture_output=True, text=True).stdout
        os.remove("temp.go")
        return result

    def _execute_shell(self, code):
        return subprocess.run(["bash", "-c", code], capture_output=True, text=True).stdout

    def _execute_groovy(self, code):
        with open("temp.groovy", "w") as f:
            f.write(code)
        result = subprocess.run(["groovy", "temp.groovy"], capture_output=True, text=True).stdout
        os.remove("temp.groovy")
        return result

    def _execute_kotlin(self, code):
        with open("temp.kt", "w") as f:
            f.write(code)
        subprocess.run(["kotlinc", "temp.kt", "-include-runtime", "-d", "temp.jar"], check=True)
        result = subprocess.run(["java", "-jar", "temp.jar"], capture_output=True, text=True).stdout
        os.remove("temp.kt")
        os.remove("temp.jar")
        return result

    def _execute_scala(self, code):
        with open("temp.scala", "w") as f:
            f.write(code)
        result = subprocess.run(["scala", "temp.scala"], capture_output=True, text=True).stdout
        os.remove("temp.scala")
        return result
