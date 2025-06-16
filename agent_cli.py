import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
import subprocess

# Load environment variables
load_dotenv()

# --- Gemini Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Agent Tools ---

def read_file(filepath: str) -> str:
    """Reads the content of a file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        print(f"Tool: read_file('{filepath}') -> Success (read {len(content)} bytes)")
        return content
    except FileNotFoundError:
        print(f"Tool: read_file('{filepath}') -> Error: File not found.")
        return f"Error: File '{filepath}' not found."
    except Exception as e:
        print(f"Tool: read_file('{filepath}') -> Error: {e}")
        return f"Error reading file '{filepath}': {e}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file, overwriting if it exists."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure directory exists
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Tool: write_file('{filepath}') -> Success (wrote {len(content)} bytes)")
        return f"File '{filepath}' written successfully."
    except Exception as e:
        print(f"Tool: write_file('{filepath}') -> Error: {e}")
        return f"Error writing file '{filepath}': {e}"

def list_directory(path: str = '.') -> str:
    """Lists files and directories in the given path."""
    try:
        items = os.listdir(path)
        dir_contents = []
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                dir_contents.append(f"{item}/")
            else:
                dir_contents.append(item)
        print(f"Tool: list_directory('{path}') -> Success")
        return "\n".join(dir_contents)
    except FileNotFoundError:
        print(f"Tool: list_directory('{path}') -> Error: Directory not found.")
        return f"Error: Directory '{path}' not found."
    except Exception as e:
        print(f"Tool: list_directory('{path}') -> Error: {e}")
        return f"Error listing directory '{path}': {e}"

def execute_command(command: str) -> str:
    """Executes a shell command and returns its stdout/stderr."""
    try:
        # For security, you might want to whitelist commands or confirm with user
        print(f"Tool: execute_command('{command}') -> Running...")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False # Do not raise exception for non-zero exit codes
        )
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        print(f"Tool: execute_command('{command}') -> Done. Exit Code: {result.returncode}")
        return output
    except Exception as e:
        print(f"Tool: execute_command('{command}') -> Error: {e}")
        return f"Error executing command '{command}': {e}"

# Map tool names to functions
TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "execute_command": execute_command,
}

# --- Agent Core Logic ---

SYSTEM_PROMPT = """
You are an AI code assistant designed to help modify, implement, and debug Python projects.
You have access to a set of tools to interact with the file system and execute commands.

Your goal is to understand the user's request, plan the necessary changes, and use your tools to implement them.
Think step-by-step and show your reasoning.

You MUST use the following format for your responses:

Thought: Your internal thought process for planning and reasoning.
Tool: <tool_name>(<arg1>=<value1>, <arg2>=<value2>, ...)
Observation: The output from the tool execution.
... (repeat Thought/Tool/Observation until task is complete)
Final Answer: A summary of what you did and confirmation that the task is complete.

Available Tools:
- read_file(filepath: str) -> str: Reads the content of a file.
- write_file(filepath: str, content: str) -> str: Writes content to a file, overwriting if it exists.
- list_directory(path: str = '.') -> str: Lists files and directories in the given path.
- execute_command(command: str) -> str: Executes a shell command and returns its stdout/stderr.

Example interaction:
User: List the files in the current directory.
Thought: The user wants to see the files. I should use the `list_directory` tool.
Tool: list_directory()
Observation: requirements.txt
main.py
...
Final Answer: I have listed the files for you.

When asked to modify code, always read the relevant files first.
When you are done, provide a clear "Final Answer".
Be concise with your "Thought" and "Final Answer" sections.
"""

def run_agent_chat():
    print("Welcome to the Gemini Code Agent CLI!")
    print("Type 'exit' to quit.")
    print("Enter your requests below.")

    history = []
    history.append({"role": "user", "parts": SYSTEM_PROMPT})
    # Initial prompt for the AI to understand the context and be ready
    history.append({"role": "model", "parts": "Okay, I'm ready. What would you like to do?"})

    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() == 'exit':
            break

        # Append user input to history
        history.append({"role": "user", "parts": user_input})

        try:
            # Send conversation history to Gemini
            convo = model.start_chat(history=history)
            response = convo.send_message(user_input)
            response_text = response.text
            print("\nAgent:")
            print(response_text)

            # --- Parse Agent's Response and Execute Tools ---
            tool_match = re.search(r"Tool: (\w+)\((.*)\)", response_text)
            final_answer_match = re.search(r"Final Answer: (.*)", response_text, re.DOTALL)

            if tool_match:
                tool_name = tool_match.group(1)
                tool_args_str = tool_match.group(2)
                args = {}

                # Parse arguments (simple key=value parsing)
                for arg_pair in tool_args_str.split(','):
                    if '=' in arg_pair:
                        key, value = arg_pair.split('=', 1)
                        # Remove quotes from string values and convert to native types if possible
                        value = value.strip()
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        elif value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        args[key.strip()] = value

                if tool_name in TOOL_MAP:
                    tool_func = TOOL_MAP[tool_name]
                    observation = tool_func(**args)
                    # Append tool output as an "Observation" for the AI's next turn
                    history.append({"role": "user", "parts": f"Observation:\n{observation}"})
                    # Re-run the model with the observation
                    continue # Continue the loop to let the agent process the observation

                else:
                    print(f"Agent requested unknown tool: {tool_name}")
                    history.append({"role": "user", "parts": f"Observation:\nError: Unknown tool '{tool_name}'"})
            elif final_answer_match:
                print(f"Agent finished: {final_answer_match.group(1).strip()}")
                # Reset history for a new task, or decide to keep it for multi-step conversations
                # For this simple CLI, we'll keep the history. If you want a fresh start per prompt, clear it.
            else:
                print("Agent did not provide a recognized tool call or final answer. Continuing conversation.")
                # If the agent just provides a thought or asks a question, we continue
                pass # The response itself is already printed, so nothing more to do

            # Append agent's full response to history for context
            history.append({"role": "model", "parts": response_text})

        except Exception as e:
            print(f"An error occurred: {e}")
            history.append({"role": "user", "parts": f"Error: An internal error occurred: {e}"}) # Let agent know

if __name__ == "__main__":
    run_agent_chat()