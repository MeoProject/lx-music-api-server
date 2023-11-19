# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: variable.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

import os


debug_mode = True
log_length_limit = 100000
running = True
config = {}
workdir = os.getcwd()
banList_suggest = 0
iscn = True
fake_ip = None