import questionary
import subprocess
import os
import platform

def run_command(command):
    if platform.system() == "Windows":
        if command[0] in {"npx", "npm", "nuxi"}:
            command[0] += ".cmd"
        subprocess.run(command, shell=True)
    else:
        subprocess.run(command)

def handle_frontend():
    frontend_choice = questionary.select(
        "Select Frontend Technology:",
        choices=["React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "SolidJS", "Qwik", "Astro"]
    ).ask()

    frontend_lang = None
    if frontend_choice == "React":
        frontend_lang = questionary.select(
            "Choose language for React:",
            choices=["JavaScript", "TypeScript"]
        ).ask()

    print("\nCreating frontend...")

    if frontend_choice == "React":
        if frontend_lang == "JavaScript":
            run_command(["npx", "create-react-app", ".", "--template", "cra-template"])
        else:
            run_command(["npx", "create-react-app", ".", "--template", "typescript"])
    elif frontend_choice == "Next.js":
        next_lang = questionary.select(
            "Choose language for Next.js:",
            choices=["JavaScript", "TypeScript"]
        ).ask()

        if next_lang == "TypeScript":
            run_command(["npx", "create-next-app", ".", "--typescript"])
        else:
            run_command(["npx", "create-next-app", "."])
    elif frontend_choice == "Vue":
        run_command(["npm", "init", "vue@latest"])
    elif frontend_choice == "Angular":
        run_command(["npx", "@angular/cli", "new", os.getcwd()])
    elif frontend_choice == "Svelte":
        run_command(["npm", "create", "vite@latest", ".", "--", "--template", "svelte"])
    elif frontend_choice == "Nuxt.js":
        run_command(["npx", "nuxi", "init", "."])
    elif frontend_choice == "SolidJS":
        run_command(["npm", "create", "solid@latest"])
    elif frontend_choice == "Qwik":
        run_command(["npm", "create", "qwik@latest"])
    elif frontend_choice == "Astro":
        run_command(["npm", "create", "astro@latest"])
