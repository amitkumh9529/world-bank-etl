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

# =========================================================
# LOGGING FUNCTION
# =========================================================

def log_progress(message):

    timestamp_format = "%Y-%m-%d %H:%M:%S"

    now = datetime.now()

    timestamp = now.strftime(timestamp_format)

    with open(LOG_FILE, "a") as f:
        f.write(timestamp + " : " + message + "\n")

# =========================================================
# EXTRACT FUNCTION
# =========================================================

def extract(url, table_attribs):

    html_page = requests.get(url).text

    soup = BeautifulSoup(html_page, "html.parser")

    df = pd.DataFrame(columns=table_attribs)

    tables = soup.find_all("tbody")

    rows = tables[0].find_all("tr")

    for row in rows:

        col = row.find_all("td")

        if len(col) != 0:

            data_dict = {
                "Name": col[1].find_all("a")[1]["title"],
                "MC_USD_Billion": float(col[2].contents[0][:-1])
            }

            temp_df = pd.DataFrame(data_dict, index=[0])

            df = pd.concat([df, temp_df], ignore_index=True)

    return df

# =========================================================
# TRANSFORM FUNCTION
# =========================================================

def transform(df, exchange_rate_csv):

    exchange_rate_df = pd.read_csv(exchange_rate_csv)

    exchange_rate_df.set_index("Currency", inplace=True)

    GBP_rate = exchange_rate_df.loc["GBP", "Rate"]

    EUR_rate = exchange_rate_df.loc["EUR", "Rate"]

    INR_rate = exchange_rate_df.loc["INR", "Rate"]

    df["MC_GBP_Billion"] = np.round(
        df["MC_USD_Billion"] * GBP_rate,
        2
    )

    df["MC_EUR_Billion"] = np.round(
        df["MC_USD_Billion"] * EUR_rate,
        2
    )

    df["MC_INR_Billion"] = np.round(
        df["MC_USD_Billion"] * INR_rate,
        2
    )

    return df

# =========================================================
# LOAD TO CSV FUNCTION
# =========================================================

def load_to_csv(df, output_path):

    df.to_csv(output_path, index=False)

# =========================================================
# LOAD TO DATABASE FUNCTION
# =========================================================

def load_to_db(df, sql_connection, table_name):

    df.to_sql(
        table_name,
        sql_connection,
        if_exists="replace",
        index=False
    )


# =========================================================
# RUN QUERY FUNCTION
# =========================================================

def run_query(query_statement, sql_connection):

    print("\nQUERY:")
    print(query_statement)

    query_output = pd.read_sql(query_statement, sql_connection)

    print("\nQUERY OUTPUT:")
    print(query_output)

    log_progress("Query executed successfully")


# =========================================================
# MAIN ETL PIPELINE
# =========================================================

def main():

    log_progress("ETL Job Started")

    # ---------------- EXTRACT ----------------

    log_progress("Extract phase Started")

    extracted_df = extract(URL, TABLE_ATTRIBS)

    print("\nExtracted Data:")
    print(extracted_df.head())

    log_progress("Extract phase Ended")

    # ---------------- TRANSFORM ----------------

    log_progress("Transform phase Started")

    transformed_df = transform(
        extracted_df,
        EXCHANGE_RATE_CSV
    )

    print("\nTransformed Data:")
    print(transformed_df.head())

    log_progress("Transform phase Ended")

    # ---------------- LOAD ----------------

    log_progress("Load phase Started")

    load_to_csv(
        transformed_df,
        OUTPUT_CSV_PATH
    )

    sql_connection = sqlite3.connect(DATABASE_NAME)

    load_to_db(
        transformed_df,
        sql_connection,
        TABLE_NAME
    )

    log_progress("Load phase Ended")

    # ---------------- QUERY ----------------

    query_statement_1 = f"""
    SELECT * FROM {TABLE_NAME} LIMIT 5
    """

    run_query(query_statement_1, sql_connection)

    query_statement_2 = f"""
    SELECT Name
    FROM {TABLE_NAME}
    ORDER BY MC_USD_Billion DESC
    LIMIT 5
    """

    run_query(query_statement_2, sql_connection)

    # ---------------- CLOSE CONNECTION ----------------

    sql_connection.close()

    log_progress("Database connection closed")

    log_progress("ETL Job Ended Successfully")

# =========================================================
# DRIVER CODE
# =========================================================

if __name__ == "__main__":
    main()