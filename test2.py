import os
import pathlib

src_path = pathlib.Path(__file__).parent.absolute().as_posix()
src_path2 = "./src"
directory = "commands"


COMMANDS = [
    print(f"src.{root.replace(f'{src_path2}/', '')}.{ext.replace('.py', '')}")
    for root, dirs, files in os.walk(f"{src_path2}/{directory}")
    for ext in files
    if ext.endswith(".py")
]

# for root, dirs, files in os.walk(f"{src_path}/{directory}"):
#     for file in files:
#         if file.endswith(".py"):
#             print(f"src.{root.replace(f'{src_path}/', '')}.{file.replace('.py', '')}")