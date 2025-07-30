import os
import sys

def prompt_yes_no(prompt):
    while True:
        response = input(f"{prompt} (y/N): ").strip().lower()
        if response == "":
            return False  # default to 'n'
        if response in ("y", "n"):
            return response == "y"
        print("Please enter 'y' or 'n'.")

def prompt_int(prompt, default, min_val, max_val):
    while True:
        response = input(f"{prompt} [{default}]: ").strip()
        if not response:
            return default
        if response.isdigit():
            val = int(response)
            if min_val <= val <= max_val:
                return val
        print(f"Please enter a number between {min_val} and {max_val}.")

def prompt_port(prompt, default):
    while True:
        response = input(f"{prompt} [{default}]: ").strip()
        if not response:
            return default
        if response.isdigit() and 1 <= int(response) <= 65535:
            return int(response)
        print("Please enter a valid port number (1–65535).")

def parse_args():
    files_dir = os.getcwd()  # Current working directory
    print(f"[INFO] Serving files from: {files_dir}")

    verbose = prompt_yes_no("Enable verbose logging?")
    batch_size = prompt_int("Enter batch size", default=5, min_val=1, max_val=20)
    http_port = prompt_port("HTTP port", default=8000)
    udp_port = prompt_port("UDP port", default=5757)

    class Args:
        pass

    args = Args()
    args.verbose = verbose
    args.batch_size = batch_size
    args.http_port = http_port
    args.udp_port = udp_port
    args.directory = files_dir

    return args, files_dir
