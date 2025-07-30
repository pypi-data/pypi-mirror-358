"""
Configuration settings for the conventions package.
"""
import os
from typing import Dict, Any, List

# Base directory for storing package data
HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME_DIR, ".conventions")

# Cache settings
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_MAX_AGE_HOURS = 24  # How long to keep cached conference data

# Conference definitions
CONFERENCES = {
    "ICRA25": {
        "name": "IEEE International Conference on Robotics and Automation 2025",
        "url": "https://ras.papercept.net/conferences/conferences/ICRA25/program/ICRA25_ProgramAtAGlanceWeb.html",
        "dates": "May 19-23, 2025",
        "location": "Atlanta, USA"
    },
    "IROS25": {
        "name": "IEEE/RSJ International Conference on Intelligent Robots and Systems 2025",
        "url": "http://irmv.sjtu.edu.cn/iros2025/",
        "dates": "Oct 19-25, 2025",
        "location": "Hangzhou, China"
    },
    "HUMANOIDS25": {
        "name": "IEEE-RAS 24th International Conference on Humanoid Robots 2025",
        "url": "http://2025.ieee-humanoids.org/",
        "dates": "Sep 30 - Oct 2, 2025",
        "location": "Seoul, Korea (South)"
    }
}

# Output formatting
MAX_RESULTS = 50  # Maximum number of results to show
SHOW_URL = True  # Whether to show URLs in search results 