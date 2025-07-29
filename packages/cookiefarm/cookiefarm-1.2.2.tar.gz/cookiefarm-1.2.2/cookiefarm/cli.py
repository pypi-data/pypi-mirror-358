import os
import sys
import subprocess

def main():
    base_dir = os.path.dirname(__file__)
    binary_path = os.path.join(base_dir, "bin", "ckc")

    if not os.path.exists(binary_path):
        print(f"Binary not found at {binary_path}")
        exit(1)

    subprocess.run([binary_path] + sys.argv[1:])
