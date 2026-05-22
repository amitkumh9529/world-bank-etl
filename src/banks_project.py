# banks_project.py

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import sqlite3
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------

url = "https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks"

table_attribs = ["Name", "MC_USD_Billion"]

csv_path = "./Largest_banks_data.csv"

db_name = "Banks.db"

table_name = "Largest_banks"

log_file = "code_log.txt"

exchange_rate_path = "exchange_rate.csv"