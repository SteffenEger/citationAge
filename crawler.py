import os
import types
import json
import pandas as pd
import arxiv
from sickle import Sickle
from datetime import datetime, date
import time
from semanticscholar import  SemanticScholar
from semanticscholar.Paper import Paper
from tqdm import tqdm
import re

def _get_papers(
        self,
        paper_ids,
        fields: list = None
):
    # Overwriting this method of the python semanticscholar API and allow papers that exist in arxiv but not semantic scholar
    if not fields:
        fields = Paper.SEARCH_FIELDS

    url = f'{self.api_url}/paper/batch'

    fields = ','.join(fields)
    parameters = f'&fields={fields}'

    payload = {"ids": paper_ids}

    data = self._requester.get_data(
        url, parameters, self.auth_header, payload)
    papers = [Paper(item) if item else None for item in data]

    return papers


sch = SemanticScholar(timeout=100)
# Overwrite function with hotfix
sch.get_papers = types.MethodType(_get_papers, sch)

def get_reference(id):
    """
    influentialCitationCount
    citationCount
    referenceCount

    :param batch_ids:
    :return:
    """
    # Add the arxiv prefix to the ids
    id = f"arxiv:{id}"
    try:
        raw_ref = sch.get_paper_references(paper_id=id,
                                                 # fields=["paperId",
                                                 #         "title",
                                                 #         "year",
                                                 #         "citationCount",
                                                 #         "influentialCitationCount",
                                                 #         "isInfluential"
                                                 #         ]
                                        )
        # Post-processing result from Semantic Scholar
        ref = []
        if raw_ref:
            for item in raw_ref:
                if item["citedPaper"]["paperId"] is not None:
                    item["citedPaper"]["isInfluential"] = item["isInfluential"]
                    ref.append(item["citedPaper"])
            return ref
        else:
            return []
    except:
        return []

def harvest_meta_data(fr = '2013-01-01', un= '2013-02-01'):
    URL = "http://export.arxiv.org/oai2"
    sickle = Sickle(URL,
                    max_retries=10,
                    default_retry_after=10)

    subject = 'cs'
    year, month, day = fr.split('-')
    year, month, day = int(year), int(month), int(day)
    fr_dt = date(year, month, day)
    year, month, day = un.split('-')
    year, month, day = int(year), int(month), int(day)
    un_dt = date(year, month, day)

    papers = []
    while True:
        records = sickle.ListRecords(
            **{'metadataPrefix': 'arXiv',
               'from': f'{fr}',
               'until': f'{un}',
               'ignore_deleted': True,
               'set': f'{subject}'
               })

        date_list, author_length_list, subject = [], [], []
        for i, record in enumerate(records):
            #id created updated
            publishedTime = datetime.strptime(record.metadata["created"][0], "%Y-%m-%d" ).date()
            if fr_dt <= publishedTime < un_dt:
                json_entry  = { "id": record.metadata["id"],
                                "title": record.metadata["title"],
                                "cat": record.metadata["categories"]}
                papers.append(json_entry)
        time.sleep(50)
        try:
            records.next()
        except:
            break
    return papers

def load_metadata(cat, year):
    with open(f"data/{cat}/{year}/{cat}_{year}.json", "r") as fp:
        content = json.load(fp)
    return content

def get_batch_ids(papers):
    ids = []
    for item in papers:
        ids.extend(item["id"] )
    return ids

def harvest_reference(cat, year):
    # Load saved paper metadata from local drive
    papers = load_metadata(cat, year)
    ids = get_batch_ids(papers)

    results = []

    for i, id in enumerate(tqdm(ids)):
        if i % 500 == 0:
            time.sleep(20)
        references = get_reference(id)
        results.append({"id": id,
                        "reference": references})
    return results

def post_processing_cs_oai_data():
    _ids = []
    files = os.listdir("data/cs")
    for file in files:
        with open(f"data/cs/{file}", "r", encoding="utf-8") as fp:
            content = json.load(fp)
            for item in content:
                cats = item["cat"][0].split(" ")
                if "cs.CL" in cats:
                    _ids.append([item["id"], cats])

    year_id = {}
    for id, cats in _ids:
        year = "20"+id[0].split(".")[0][:-2]
        if year not in year_id.keys():
            year_id[year] = [{"id": id[0], "cat": cats}]
        else:
            year_id[year].append({"id": id[0], "cat": cats})

    for year, ids in year_id.items():
        with open(f"data/cs.CL/cs.CL_{year}.json", "w") as fp:
            json.dump(year_id[year],fp)

if __name__ == "__main__":
    # Harvest data with oai
    # cats = [
    #         #"econ.EM",
    #         #"cs.LG",
    #         #"cs.AI",
    #         #"cs.CV",
    #         #"hep-th"
    # ]
    # date_range = pd.date_range('2023-06-01', '2023-08-01',freq='MS').strftime("%Y-%m-%d").tolist()
    # fr_un = []
    # for i in range(len(date_range)-1):
    #     fr_un.append([date_range[i], date_range[i+1]])
    # for item in fr_un:
    #     papers = harvest_meta_data(fr=item[0], un=item[1])
    #     with open(f"data/cs_{item[0]}_{item[1]}.json", "w") as fp:
    #         json.dump(papers, fp, indent=4)


    # for year in range(2013, 2024):
    #     print(f"Fetching paper references from cat:hep-th in {year}")
    #     result = harvest_reference("hep-th", year)
    #     time.sleep(50)
    #     with open(f"data/hep-th/{year}/output_influential.json", "w") as fp:
    #         json.dump(result, fp, indent=4)

    # Harvest data with arvix api
    # start_year = 2023
    # title = []
    # for result in search():
    #     if result.published.year >= 2013:
    #         title.append({'title': result.title, 'id': result.entry_id.split("/")[-1]})
    #     else:
    #         break
    #     if result.published.year < start_year:
    #         start_year = result.published.year
    #         print(f"Fetching data from {start_year}")
    #     if len(title) % 500 == 0:
    #         print(f"Number of fetched papers: {len(title)}")
    # with open(f"data/cs.LG/cs.LG_2013_2023.json", "w") as fp:
    #     json.dump(title, fp, indent=4)

    # cat = "econ.EM"
    # for year in range(2021, 2022):
    #     print(f"Start fetching reference from {year}")
    #     results = []
    #     df = pd.read_csv(f"data/{cat}/{year}/output_{year}_new.csv", header=0, index_col=0)
    #
    #     for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    #         if index % 500 == 0:
    #             time.sleep(20)
    #         id = row["link"].replace("http://arxiv.org/abs/","").split("v")[0]
    #         references = get_reference(id)
    #         results.append({"id": id, "reference": references})
    #
    #     with open(f"data/{cat}/{year}/output.json", "w") as fp:
    #         json.dump(results,fp, indent=4)

    non_cs_cats = [
        'math.AP',
        'hep-ph',
        'econ.GN',  # (General Economics) Economics
        'eess.SP',  # (Signal Processing) Electrical Engineering and Systems Science
        'q-bio.PE',  # (Populations and Evolution) Quantitative Biology
        'q-fin.ST',  # (Statistical Finance) Quantitative Finance
        'stat.ME' # (Methodology) Statistics
    ]

    with open(os.path.join(os.path.dirname(os.getcwd()), f"citationAge/data/categorization/non_cs.json"), "r") as fp:
        content = json.load(fp)

    for cat in non_cs_cats:
        for year in range(2013, 2023):
            results = []
            ids = content[cat][str(year)]
            for i, id in enumerate(tqdm(ids)):
                if i % 500 == 0:
                    time.sleep(20)
                references = get_reference(id)
                results.append({"id": id, "reference": references})
            with open(f"data/{cat}/{year}/output.json", "w") as fp:
                json.dump(results,fp, indent=4)





