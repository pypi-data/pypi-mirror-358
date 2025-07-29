import os, shutil
from pathlib import Path

cwd = os.getcwd()
tmp_dir = cwd + "/tmp"
logger_dir = cwd + "/log"

os.makedirs(tmp_dir, exist_ok=True)
os.makedirs(logger_dir, exist_ok=True)


def clean_directories():
    clean_directory(tmp_dir)


def clean_directory(dir_path: str):
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                shutil.rmtree(dir_path)  # Recursively remove directories
    else:
        Exception(f"Directory {dir_path} does not exist.")
