import types
import json
from sickle import Sickle
from datetime import datetime, date
import time
from semanticscholar import  SemanticScholar
from semanticscholar.Paper import Paper


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
        raw_ref = list(sch.get_paper_references(paper_id=id,
                                                 fields=["paperId",
                                                         "title",
                                                         "year",
                                                         "citationCount",
                                                         "influentialCitationCount"]
                                        ))
        # Post-processing result from Semantic Scholar
        if raw_ref:
            ref = [item["citedPaper"] for item in raw_ref if item["citedPaper"]["paperId"] is not None]
            return ref
        else:
            return []
    except:
        return []


def harvest_meta_data():
    URL = "http://export.arxiv.org/oai2"
    sickle = Sickle(URL,
                    max_retries=10,
                    default_retry_after=10)

    subject = 'physics:hep-th'
    fr = '2019-01-01'
    year, month, day = fr.split('-')
    year, month, day = int(year), int(month), int(day)
    fr_dt = date(year, month, day)
    un = '2019-12-31'
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
            if fr_dt < publishedTime < un_dt:
                json_entry  = { "id": record.metadata["id"],
                                "title": record.metadata["title"]}
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

    for id in ids:
        references = get_reference(id)
        #times.sleep(1)
        results.append({"id": id,
                        "reference": references})
    return results


if __name__ == "__main__":
    # cats = [
    #         #"econ.EM",
    #         #"cs.LG",
    #         #"cs.AI",
    #         #"cs.CV",
    #         "hep-th"
    # ]
    # papers = harvest_meta_data()
    # with open(f"data/hep-th_2018.json", "w") as fp:
    #     json.dump(papers, fp, indent=4)

    for year in range(2013, 2014):
        result = harvest_reference("hep-th", year)
        time.sleep(50)
        with open(f"data/hep-th/{year}/output.json", "w") as fp:
            json.dump(result, fp, indent=4)


