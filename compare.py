import json
import arxiv
import pandas as pd
import os
import logging
import random
import statistics
from sanity_check import PaperPDFParser, get_entry_id_from_url
from tqdm import tqdm

def choose_random_id(len_samp, num_samp):
    if len_samp < num_samp:
        return [i for i in range(len_samp)]
    else:
        ids = [i for i in range(len_samp)]
        results  = random.sample(ids, num_samp)
        return results

def count_citation_pdf_parse(topic, main_year, num_samp):
    pdfParser = PaperPDFParser()

    # Read papers data for a year
    df = pd.read_csv(f"data/{topic}/{main_year}/output_{main_year}_new.csv")

    # Choose n random document ids to process
    ids = choose_random_id(len(df), num_samp)
    # Save the ids we choose
    with open(f"data/{topic}/{main_year}/science_parse_selected.json", "w") as fp:
        json.dump({"ids": ids}, fp)

    results = {}
    for id, row in tqdm(df.iterrows()):
        if id in ids:
            try:
                entry_id = get_entry_id_from_url(row["link"])
                title = row["title"]
                logging.info(f"Start processing {title}")

                # Download paper from arxiv
                paper = next(arxiv.Search(id_list=[entry_id]).results())
                if os.path.exists(f"./data/{topic}/{main_year}/pdf/{title}.pdf") == False:
                    paper.download_pdf(dirpath=f"./data/{topic}/{main_year}/pdf", filename=f"{title}.pdf")

                # Parse the data of the paper from pdf
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

    with open(f"data/{topic}/{main_year}/statistics_pdfparse_500.csv", "w") as fp:
        json.dump({"mean":mean, "mode": mode, "median": median}, fp)

    return mean, mode

if __name__ == "__main__":
    # cs.SI
    # math.GM
    # cs.DM
    # cs.DL
    # cs.CV 2013-2019
    # cs.LG 2013-2016
    cats = ["math.GM", "cs.SI", "cs.DM", "cs.DL"]
    for cat in cats:
        for year in range(2013, 2024):
            print(f"processing documents of year {year} for cat {cat}")
            if year != 2017 and cat != "cs.SI":
                count_citation_pdf_parse(cat, main_year=year, num_samp=500)
                print("Finished year {year} for cat {cat}")

    # cs.CV
    for year in range(2013, 2020):
        print(f"processing documents of year {year} for cat cs.CV")
        count_citation_pdf_parse("cs.CV", main_year=year, num_samp=500)
        print("Finished year {year} for cat {cat}")

    # cs.LG
    for year in range(2013, 2017):
        print(f"processing documents of year {year} for cat cs.LG")
        count_citation_pdf_parse("cs.LG", main_year=year, num_samp=500)
        print("Finished year {year} for cat {cat}")

    # cs.AI
    # hep-th