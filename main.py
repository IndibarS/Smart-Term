import os
import datetime
import json
import getpass
from groq import Groq
import socket
import subprocess
import shlex

def is_command_valid(command):
    """
    Checks if a terminal command is valid without running it.
    Returns True if the command is valid, False otherwise.
    """
    cmd_parts = shlex.split(command)
    cmd_path = which(cmd_parts[0])
    return cmd_path is not None

def which(program):
    """
    Mimics the Unix 'which' command to find the path of an executable.
    Returns the path if the executable is found, None otherwise.
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def execute_command(command):
    """
    Executes a command and returns its output.
    Handles 'cd' command specially.
    """
    cmd_parts = shlex.split(command)
    if cmd_parts[0] == 'cd':
        try:
            os.chdir(os.path.expanduser(cmd_parts[1]) if len(cmd_parts) > 1 else os.path.expanduser('~'))
            return ""
        except FileNotFoundError:
            return f"cd: {cmd_parts[1]}: No such file or directory"
    else:
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error executing command: {str(e)}"

def get_multiline_input():
    """
    Allows for multi-line input until a line with only a period is entered.
    """
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == '.':
                break
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines)

client = Groq(api_key="PASTE_YOUR_GROQ_API_KEY_HERE")
user = os.getlogin()
host = socket.gethostname()

while True:
    status = os.system("echo $status")
    try:
        prompt = input(f"\u001b[0;32m{user}\u001b[0m@{host} \u001b[0;32m~{os.getcwd()} \u001b[0;31m[{status}]\u001b[0m > ")
        if prompt.endswith('\\'):
            prompt = prompt[:-1] + '\n' + get_multiline_input()
    except EOFError:
        print("\n\n\u001b[0;35mThanks for using SmarTerm!\u001b[0m\n")
        break

    if prompt.strip() == "":
        continue

    if is_command_valid(prompt.split()[0]) or prompt.split()[0] == 'cd':
        print(f"\n\u001b[0;35mRunning: {prompt}\u001b[0m\n")
        output = execute_command(prompt)
        if output:
            print(output)
    else:
        ai_command = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": f"You are a command-line interface assistant. Provide only the exact command to execute the user's request, without any explanations or markdown. If you can't provide a command, respond with 'None'.",
            }, {
                "role": "user",
                "content": prompt,
            }],
            model="llama3-70b-8192",
        )
        ai_response = ai_command.choices[0].message.content.strip()
        if ai_response != 'None':
            print(f"\n\u001b[0;35mRunning: {ai_response}\u001b[0m\n")
            output = execute_command(ai_response)
            if output:
                print(output)
        else:
            ai_reply = client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": f"You are SmarTerm, a terminal assistant created by Indibar Sarkar. The date and time is {datetime.datetime.now()}. You are talking to {user}.",
                }, {
                    "role": "user",
                    "content": prompt,
                }],
                model="llama3-70b-8192",
            )
            print(f"\n\u001b[0;35m{ai_reply.choices[0].message.content}\u001b[0m")