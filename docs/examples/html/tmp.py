# Create a list of all files in this file's directory that end with .py

import os
import pathlib

# Get the current directory
current_directory = pathlib.Path(__file__).parent

# Get all files in the current directory
files = os.listdir(current_directory)

# Filter the files to only include .py files
py_files = [file for file in files if file.endswith(".html")]

# Rename the files on disk
for file in py_files:
    os.rename(current_directory / file, current_directory / file.replace("-", "_"))
