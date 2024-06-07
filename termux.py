# for installing the dependencies on Termux.
# ruamel-yaml-clib need to build from source, but it will throw an error during 
# the build process in default configuration. To fix this, we need to set 
# CFLAGS environment variable to "-Wno-incompatible-function-pointer-types".
# Resolution from: https://github.com/termux/termux-packages/issues/16746

import os
import subprocess

def is_termux():
    return "termux" in os.environ.get("HOME", "")

def install_ruamel_clib():
    if (is_termux()):
        # https://github.com/termux/termux-packages/issues/16746
        os.environ["CFLAGS"] = "-Wno-incompatible-function-pointer-types"
        subprocess.run(["poetry", "run", "pip", "install", "ruamel-yaml-clib"])

def install():
    install_ruamel_clib()
    subprocess.run(["poetry", "install"])

if __name__ == "__main__":
    install()