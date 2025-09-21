import os
import shutil

REMOVE_DIRS = ["logs", "data/cache"]
REMOVE_FILES = ["data.db"]


def remove(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_dir = os.path.join(dirpath, "__pycache__")
            print(f"Deleting(1/3) {pycache_dir}")
            shutil.rmtree(pycache_dir, ignore_errors=True)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dir in REMOVE_DIRS:
            if dir in dirnames:
                shutil.rmtree(
                    os.path.join(os.path.dirname(__file__), dir), ignore_errors=True
                )
                print(f"Deleting(2/3) {dir}")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in REMOVE_FILES:
            if file in filenames:
                os.remove(f"data/{file}")
                print(f"Deleting(3/3) {file}")


if __name__ == "__main__":
    remove(".")
