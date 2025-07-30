"""Settings."""

import logging as lg

import requests_cache

# core
STATIONS_ID_COL = "station_id"
TIME_COL = "time"
SJOIN_KWARGS = {"how": "inner", "predicate": "intersects"}

# qc
ATMOSPHERIC_LAPSE_RATE = 0.0065
OUTLIER_LOW_ALPHA = 0.01
OUTLIER_HIGH_ALPHA = 0.95
STATION_OUTLIER_THRESHOLD = 0.2
STATION_INDOOR_CORR_THRESHOLD = 0.9
UNRELIABLE_THRESHOLD = 0.2

# utils
REQUEST_KWARGS = {}
# PAUSE = 1
ERROR_PAUSE = 60
# TIMEOUT = 180
## cache
USE_CACHE = True
CACHE_NAME = "meteora-cache"
CACHE_BACKEND = "sqlite"
CACHE_EXPIRE = requests_cache.NEVER_EXPIRE

## logging
LOG_CONSOLE = False
LOG_FILE = False
LOG_FILENAME = "meteora"
LOG_LEVEL = lg.INFO
LOG_NAME = "meteora"
LOGS_FOLDER = "./logs"
