import sys
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from os import listdir, makedirs
from os.path import isfile, join, exists
from zipfile import ZipFile, BadZipFile
import pandas
from io import BytesIO
import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36 Edg/89.0.774.45",
    "Accept-Language": "en-US,en;q=0.9"
}
EIA_URL = "https://www.eia.gov/electricity/data/eia923/"
MIN_YEAR = 2015
RAW_DIR = "raw"
EXT_DIR = "Extracted"


def check_dir():
    if exists(RAW_DIR):
        print(f"{RAW_DIR} directory found")
    else:
        print(f"Creating new {RAW_DIR} directory")
        makedirs(RAW_DIR)
    if exists(EXT_DIR):
        print(f"{EXT_DIR} directory found")
    else:
        print(f"Creating new {RAW_DIR} directory")
        makedirs(RAW_DIR)


def download_all_zip():
    response = requests.get(url=EIA_URL, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.title.text)
    all_anchor_tags = soup.find_all(name='a')

    downloadable_links = {}
    for link in all_anchor_tags:
        href = str(link.get("href"))
        if href.endswith(".zip"):
            year = str(link.get("title")).strip()
            if year.startswith("20"):
                year = int(year)
                if year >= MIN_YEAR:
                    downloadable_links[year] = f"{EIA_URL}{href}"

    for dl in downloadable_links:
        file_name = downloadable_links[dl].split('/')[-1]
        path_to_file = f"{RAW_DIR}/{file_name}"
        if exists(path_to_file) and dl != datetime.datetime.now().year:
            print(f"{file_name} exists")
        else:
            zip_file = requests.get(downloadable_links[dl], stream=True, headers=HEADERS)
            zip_file.raise_for_status()
            total_size = int(zip_file.headers['content-length'])
            print(f"\n{dl}: {downloadable_links[dl]} [{round(total_size/1048576, 2)} MB]")
            with open(path_to_file, mode="wb") as fb:
                for chunk in tqdm(iterable=zip_file.iter_content(chunk_size=1024),
                                  total=total_size/1024,
                                  unit=" KB",
                                  desc=f"{file_name}",
                                  dynamic_ncols=True):
                    fb.write(chunk)


def save_zip_to_csv():
    saved_files = [f for f in listdir(RAW_DIR) if isfile(join(RAW_DIR, f))]
    for file in saved_files:
        year = int(file[5:9])
        try:
            with ZipFile(f"{RAW_DIR}/{file}", "r") as zp:
                zp_files = zp.filelist
                for zp_file in zp_files:
                    if zp_file.filename.startswith("EIA923_Schedules_2_3_4_5_M"):
                        file_name_csv = f"Form923_fuel&Receipts&Costs_{file[5:9]}"
                        path_to_file = f"{EXT_DIR}/{file_name_csv}.csv"
                        new_file = True
                        excel_rows_to_skip = 3 if year == datetime.datetime.now().year else 4
                        if exists(path_to_file) and year != datetime.datetime.now().year:
                            print(f"{file_name_csv} exists")
                            new_file = False
                        else:
                            data = pandas.read_excel(BytesIO(zp.read(zp_file.filename)),
                                                  sheet_name="Page 5 Fuel Receipts and Costs",
                                                  skiprows=excel_rows_to_skip)
                            for col in data.columns:
                                data = data.rename(columns={col:col.replace("\n", " ")}, inplace=False)
                            if year == datetime.datetime.now().year and exists(path_to_file):
                                print(f"Updating {file_name_csv}")
                                old_data = pandas.read_csv(path_to_file)
                                if old_data.equals(data):
                                    print(f"No update required {file_name_csv}")
                                    new_file = False
                        if new_file:
                            data.to_csv(path_to_file, index=False)
                            print(f"{file_name_csv} saved in Extracted")
        except BadZipFile:
            with open(f"log.txt", "a") as error_log:
                error_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                error_log.write(f"{error_time} -> Error: {file} file is corrupted\n")
            print(f"Error: {file} file is corrupted")


if __name__  == "__main__":
    print(f"\nPython Version: {sys.version}\n")
    check_dir()
    download_all_zip()
    save_zip_to_csv()
