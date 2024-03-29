from selenium import webdriver
import pandas as pd
import json
from tqdm import tqdm
from compare import choose_random_id

import time

chromedriver_path = r"C:\Users\Nguyen\PycharmProjects\citationAgeCrawler\chromedriver_win32"
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_experimental_option(
    'prefs', {
    "download.default_directory": r"C:\Users\Nguyen\PycharmProjects\citationAgeCrawler\data\cs.SI\2016\pdf",
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": False,
    "plugins.plugins_disabled": ["Chrome PDF Viewer"]
    }
)

class SeleniumCrawler:
    def __init__(self, options, chromedriver_path):
        self.driver = webdriver.Chrome(chromedriver_path, options=options)

    def get_pdf(self, url):
        self.driver.get(url)


def sample_and_download(topic, main_year, num_samp):
    # Read papers data for a year
    df = pd.read_csv(f"data/{topic}/{main_year}/output_{main_year}_new.csv").to_dict('index')

    # Choose n random document ids to process
    ids = choose_random_id(len(df), num_samp)
    # Save the ids we choose
    with open(f"data/{topic}/{main_year}/science_parse_selected.json", "w") as fp:
        json.dump({"ids": ids}, fp)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option(
        'prefs', {
            "download.default_directory": r"C:\Users\NGUYEH\PycharmProjects\citationAge\data\cs.LG\2014\pdf",
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": False,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"]
        }
    )
    crawler = SeleniumCrawler(chromedriver_path, options)

    topic = "cs.LG"
    main_year = 2014
    sample_and_download(topic, main_year, num_samp=500)

    with open(f"data/{topic}/{main_year}/science_parse_selected.json", "r") as fp:
        ids = json.load(fp)["ids"]

    # Read papers data for a year
    df = pd.read_csv(f"data/{topic}/{main_year}/output_{main_year}_new.csv").to_dict('index')
    for id in tqdm(ids):
        row = df[id]
        link = row["link"]
        link = link.replace("arxiv.org", "export.arxiv.org")
        link = link.replace("abs", "pdf")
        link = link[:-2]+".pdf"
        crawler.get_pdf(link)
        time.sleep(3)