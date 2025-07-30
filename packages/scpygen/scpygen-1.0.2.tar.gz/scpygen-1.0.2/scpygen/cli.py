# CLI tool for scpygen
# Author: Chase Quinn - ShadowCoding
# Date: 2025-06-27

import time, os
from .generation import generate_flask_api

# ANSI color code constants
ANSI_GREEN = '\033[32m'
ANSI_YELLOW = '\033[33m'
ANSI_BLUE = '\033[34m'
ANSI_RED = '\033[31m'
ANSI_PINK = '\033[35m'
ANSI_RESET = '\033[0m'



def main():
    print("Welcome to " + ANSI_PINK + "scpygen CLI" + ANSI_RESET + "!")
    time.sleep(1)
    print("To generate a new project directory, choose one of the following options:")
    print(ANSI_GREEN + "1. Flask API Skeleton" + ANSI_RESET)
    choice = input("Enter your choice (1): ")
    if choice == '1' or choice == "":
        print("What is the name of your Flask API project?")
        project_name = input("Enter project name: ")
        if not project_name:
            print(ANSI_RED + "Project name cannot be empty." + ANSI_RESET)
            return main()
        print(ANSI_BLUE + f"Generating Flask project: {project_name}..." + ANSI_RESET)
        generate_flask_api.generate(os.getcwd(), project_name)
        time.sleep(1)
        print(ANSI_GREEN + "Project generated successfully!" + ANSI_RESET)
        time.sleep(1)
        print(ANSI_PINK + f"`cd {project_name}` and get started!." + ANSI_RESET)
        time.sleep(1)
    else:
        print(ANSI_RED + "Invalid choice. Please try again." + ANSI_RESET)
        return main()