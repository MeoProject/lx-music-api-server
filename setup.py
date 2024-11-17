from setuptools import setup
import toml

try:
    version = toml.load("./pyproject.toml")["tool"]["poetry"]["version"]
    description = toml.load("./pyproject.toml")["tool"]["poetry"]["description"]
except Exception:
    version = "1.0.0"
    description = "Description not available"

setup(
    name="lx_music_api_server_setup",
    version=version,
    scripts=["run.py"],
    author="helloplhm-qwq",
    author_email="helloplhm-qwq@outlook.com",
    description=description,
    url="https://github.com/helloplhm-qwq/lx-music-api-server",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
