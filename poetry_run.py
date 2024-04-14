import os
import argparse
import subprocess

def main_production():
    os.environ['CURRENT_ENV'] = 'production'
    subprocess.run(["python", "main.py"])

def main_development():
    os.environ['CURRENT_ENV'] = 'development'
    subprocess.run(["python", "main.py"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to set environment variables and run different environments.")
    parser.add_argument("environment", choices=["production", "development"], help="Specify the environment to run.")
    args = parser.parse_args()
    try:
        if args.environment == "production":
            main_production()
        elif args.environment == "development":
            main_development()
    except KeyboardInterrupt:
        pass
