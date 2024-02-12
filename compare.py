import json
import arxiv
import pandas as pd
import os
import logging
import random
import statistics
from sanity_check import PaperPDFParser, get_entry_id_from_url
from tqdm import tqdm
from selenium import webdriver
import os
import time
from analyse import normalize_age

def choose_random_id(len_samp, num_samp):
    if len_samp < num_samp:
        return [i for i in range(len_samp)]
    else:
        ids = [i for i in range(len_samp)]
        results  = random.sample(ids, num_samp)
        return results

def sample_and_download(topic, main_year, num_samp):
    # Read papers data for a year
    df = pd.read_csv(f"data/{topic}/{main_year}/output_{main_year}_new.csv").to_dict('index')

    # Choose n random document ids to process
    ids = choose_random_id(len(df), num_samp)
    # Save the ids we choose
    with open(f"data/{topic}/{main_year}/science_parse_selected.json", "w") as fp:
        json.dump({"ids": ids}, fp)

    entry_ids =[]
    for _id in ids:
        row = df[_id]
        entry_ids.append(get_entry_id_from_url(row["link"]))

    big_slow_client = arxiv.Client(
        page_size=2000,
        delay_seconds=10,
        num_retries=5
    )

    for paper in tqdm(big_slow_client.results(arxiv.Search(id_list=entry_ids))):
        try:
            if os.path.exists(f"./data/{topic}/{main_year}/pdf/{paper.title}.pdf") == False:
                paper.download_pdf(dirpath=f"./data/{topic}/{main_year}/pdf", filename=f"{paper.title}.pdf")
        except:
            logging.info(f"Failed downloading {paper.title}")
            pass

def selenium_download(url):
    DRIVER_PATH = r'C:\Users\NGUYEH\Downloads\chromedriver_win32\chromedriver.exe'
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        "download.default_directory": os.path.join(os.getcwd(), "Downloads"),
        # Set directory to save your downloaded files.
        "download.prompt_for_download": False,  # Downloads the file without confirmation.
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Disable PDF opening.
    })

    driver = webdriver.Chrome(DRIVER_PATH,options=options)  # Replace with correct path to your chromedriver executable.
    driver.get("https://arxiv.org/list/hep-lat/1902")  # Base url
    driver.find_elements(By.XPATH, "/html/body/div[5]/div/dl/dt[1]/span/a[2]")[
        0].click()  # Clicks the link that would normally open the PDF, now download. Change to fit your needs

def parse_pdf_bulk(topic, main_year):
    pdfParser = PaperPDFParser()

    # Read selected pdf
    with open(f"data/{topic}/{main_year}/science_parse_selected.json", "r") as fp:
        ids = json.load(fp)["ids"]

    # Read papers data for a year
    df = pd.read_csv(f"data/{topic}/{main_year}/output_{main_year}_new.csv").to_dict('index')
    # Processing the papers
    results = {}

    for id in tqdm(ids):
        row = df[id]
        title = row["title"]
        if os.path.exists(f"./data/{topic}/{main_year}/pdf/{title}.pdf"):
            # Parse the data of the paper from pdf
            try:
                reference_list = pdfParser.get_reference(fp=f"./data/{topic}/{main_year}/pdf/{title}.pdf")
                years_list = []
                for reference in reference_list:
                    years_list.append(reference["year"])
                results[row["link"]] = years_list
            except:
                logging.info(f"Failed processing {title}")
                pass

    citation_ages = []
    for id, item in results.items():
        for year in item:
            if year != None:
                if year < (main_year - 20):
                    citation_ages.append(20)
                elif main_year - 20 <= year <= main_year:
                    citation_ages.append(main_year-year)


    mean = statistics.mean(citation_ages)
    mode = statistics.mode(citation_ages)
    median = statistics.median(citation_ages)

    with open(f"data/{topic}/{main_year}/statistics_pdfparse_500.json", "w") as fp:
        json.dump({"mean":mean, "mode": mode, "median": median}, fp)

    return mean, mode

def parse_pdf_bulk_json(topic, main_year):
    pdfParser = PaperPDFParser()

    # Read papers data for a year
    pdfs = os.listdir(f"data/{topic}/{main_year}/pdf")

    # Processing the papers
    results = {}

    for pdf in tqdm(pdfs):
        title = pdf.replace(".pdf", "")
        # Parse the data of the paper from pdf
        try:
            reference_list = pdfParser.get_reference(fp=f"./data/{topic}/{main_year}/pdf/{pdf}")
            years_list = []
            for reference in reference_list:
                years_list.append(reference["year"])
            results[title] = years_list
        except:
            logging.info(f"Failed processing {title}")
            pass

    # Save the reference for the selected document from science parse
    with open(f"data/{topic}/{main_year}/reference_science_parse_selected.json", "w") as fp:
        json.dump(results, fp)

    citation_ages = []
    for id, item in results.items():
        for year in item:
            if year != None:
                if year < (main_year - 20):
                    citation_ages.append(20)
                elif main_year - 20 <= year <= main_year:
                    citation_ages.append(main_year-year)


    mean = statistics.mean(citation_ages)
    mode = statistics.mode(citation_ages)
    median = statistics.median(citation_ages)

    with open(f"data/{topic}/{main_year}/statistics_pdfparse_500.json", "w") as fp:
        json.dump({"mean":mean, "mode": mode, "median": median}, fp)

    return mean, mode

def calculcate_from_science_parse(cat):
    # Get id from 500
    results = []
    for threshold in [0,20,25,30]:
        for year in range(2013, 2024):
            with open(f"data/{cat}/{year}/science_parse_selected.json", "r") as fp:
                ids = json.load(fp)["ids"]

                with open(f"data/{cat}/{year}/output.json", "r") as fp:
                    content = json.load(fp)

                    selected_papers = [paper for i, paper in enumerate(content) if i in ids]
                    ref_years = []
                    for paper in selected_papers:
                        for ref in paper["reference"]:
                            ref_years.append(ref["year"])
                    ages = normalize_age(ref_years, year, 20)

                    # Calculated mean mode median
                    year_mean = statistics.mean(ages)
                    year_mode = statistics.mode(ages)
                    year_median = statistics.median(ages)

                    results.append([year, year_mean, year_mode, year_median, threshold])

    # Form dataframe from data
    df = pd.DataFrame(results, columns=["Year", "Mean", "Mode", "Median", "Threshold"])
    df.to_csv(f"data/{cat}/statistics_ss_500.csv", index=False)

def calculate_deviation(cat):
    pass

if __name__ == "__main__":
    calculcate_from_science_parse("math.GM")