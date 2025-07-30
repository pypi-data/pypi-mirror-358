import questionary
import subprocess
import os
import platform
import sys

def run_command(command):
    if platform.system() == "Windows":
        if command[0] in {"npx", "npm", "django-admin", "uvicorn", "flask", "nest"}:
            command[0] += ".cmd"
        subprocess.run(command, shell=True)
    else:
        subprocess.run(command)

def get_venv_path(tool):
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", f"{tool}.exe")
    else:
        return os.path.join("venv", "bin", tool)

def handle_backend():
    backend_choice = questionary.select(
        "Select Backend Technology:",
        choices=["FastAPI", "Django", "Express.js", "Nest.js"]
    ).ask()

    print("\nCreating backend...")

    # Create venv
    run_command([sys.executable, "-m", "venv", "venv"])

    if backend_choice == "FastAPI":
        run_command([get_venv_path("pip"), "install", "fastapi", "uvicorn"])
        with open("main.py", "w") as f:
            f.write("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""")

    elif backend_choice == "Django":
        run_command([get_venv_path("pip"), "install", "django"])
        run_command([get_venv_path("django-admin"), "startproject", "mysite"])

    elif backend_choice == "Express.js":
        run_command(["npm", "init", "-y"])
        run_command(["npm", "install", "express"])
        with open("index.js", "w") as f:
            f.write("""const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => res.send('Hello World!'));
app.listen(port, () => console.log(`App listening on port ${port}!`));
""")

    elif backend_choice == "Nest.js":
        run_command(["npm", "i", "-g", "@nestjs/cli"])
        run_command(["nest", "new", "."])
