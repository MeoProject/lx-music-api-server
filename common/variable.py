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
log_length_limit = 50000000
running = True
config = {}
pool_data = None
pool_cache = None
workdir = os.getcwd()
banList_suggest = 0