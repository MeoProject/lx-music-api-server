import os
import argparse
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to set environment variables and run different environments.")
    parser.add_argument(
        "environment",
        choices=["production", "development"],
        nargs="?",
        default="production",
        help="Specify the environment to run.",
    )
    args = parser.parse_args()
    try:
        if args.environment:
            os.environ["CURRENT_ENV"] = args.environment
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        pass
