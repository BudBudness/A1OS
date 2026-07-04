#!/usr/bin/env python3
import subprocess

def chat():
    print("A1OS Agent Online. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit': break
        try:
            result = subprocess.check_output(f"python3 gateway.py '{user_input}'", shell=True).decode()
            print(f"A1OS: {result.strip()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    chat()
