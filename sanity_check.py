import os
import json
import arxiv
import difflib
from pathlib import Path
from semanticscholar import SemanticScholar
from science_parse_api.api import parse_pdf
import pandas as pd
import logging

logging.basicConfig(filename='app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class PaperPDFParser:
    def __init__(self):
        self.host = 'http://127.0.0.1'
        self.port = '8080'

    def parse_pdf_content(self, fp):
        output_dict = parse_pdf(self.host, Path(fp) , port=self.port)
        return output_dict

    def get_reference(self, fp):
        doc_content = self.parse_pdf_content(fp)
        references = doc_content["references"]
        return references

class SemanticScholarMetadataExtractor:
    # Paper attributes
    # 'paperId', 'externalIds', 'corpusId', 'publicationVenue', 'url', 'title', 'abstract', 'venue',
    # 'year', 'referenceCount', 'citationCount', 'influentialCitationCount', 'isOpenAccess',
    # 'openAccessPdf', 'fieldsOfStudy', 's2FieldsOfStudy', 'embedding', 'tldr', 'publicationTypes',
    # 'publicationDate', 'journal', 'authors', 'citations', 'references'

    # Reference papers attribute

    def __init__(self):
        self.sch = SemanticScholar()

    def get_reference(self, arxiv_entry_id):
        try:
            references = self.sch.get_paper_references("arxiv:" + arxiv_entry_id)
        except:
            return []
        return references

    @staticmethod
    def get_published_year(paper_metadata):
        return paper_metadata["year"]

    @staticmethod
    def get_name(paper_metadata):
        return paper_metadata["title"]

    @staticmethod
    def format_ref(references):
        references_formated = []
        if len(references) > 0:
            for ref in references:
                references_formated.append(dict(ref))
        return references_formated

class ConsistencyChecker:
    @staticmethod
    def check_greater_than_published_year(references, original_paper_year):
        errors = []
        for ref in references:
            year = ref['citedPaper']['year']
            if year:
                if int(year) > int(original_paper_year):
                    errors.append([original_paper_year, year, ref['citedPaper']["title"]])
            else:
                    errors.append([original_paper_year, year, ref['citedPaper']["title"]])
        return errors

    @staticmethod
    def check_duplicate_entry(references):
        # Get the name list of the reference paper
        ref_paper_name = []
        for ref in references:
            ref_paper_name.append(ref['citedPaper']['title'])

        duplicate_pairs = []
        # Compare pairwise the paper
        for i in range(len(ref_paper_name)):
            for j in range(i + 1, len(ref_paper_name)):
                seq = difflib.SequenceMatcher(None, ref_paper_name[i].lower(), ref_paper_name[j].lower())
                if seq.ratio() > 0.75:
                    duplicate_pairs.append([ref_paper_name[i].lower(),ref_paper_name[j],seq.ratio()])
        return duplicate_pairs

    @staticmethod
    def check_reference_consistency(ref_sch, ref_metadata):
        """

        :param ref_sch:
        :param ref_metadata:
        :return:
            Difference between the reference listed by Semantic Scholar and the reference parsed from PDF
        """
        ref_sch_name = []
        ref_metadata_name = []

        for ref in ref_sch:
            ref_sch_name.append(ref['citedPaper']['title'])
        for ref in ref_metadata:
            ref_metadata_name.append(ref['title'])
        name_diff = list(set(ref_sch_name) ^ set(ref_metadata_name))
        return name_diff

    @staticmethod
    def check_year_consistency(ref_sch, ref_metadata):
        errors = []
        # Match by name then check year
        for title, sch_year in ref_sch.items():
            metadata_year = ref_metadata[title]
            if metadata_year != sch_year:
                errors.append([title, sch_year, metadata_year])
        return

def get_entry_id_from_url(url):
    """
    Separate the entry_id from the http link
    :param url:  url = "http://arxiv.org/abs/1301.4597v2"
    :return:
        - 1301.4597
    """
    return url.split("/")[-1].split('v')[0]

if __name__ == '__main__':
    topic = "cs.DL"
    year = "2013"
    df = pd.read_csv(f"data/{topic}/{year}/output_{year}_new.csv")

    pdfParser = PaperPDFParser()
    sch_metadataExtractor= SemanticScholarMetadataExtractor()
    checker = ConsistencyChecker()

    for id, row in df.iterrows():
        results = {}
        entry_id = get_entry_id_from_url(row["link"])
        title = row["title"]
        logging.info(f"Start processing {title}")
        # Download paper from arxiv
        paper = next(arxiv.Search(id_list=[entry_id]).results())

        try:
            if os.path.exists(f"./data/{topic}/{year}/pdf/{title}.pdf") == False:
                paper.download_pdf(dirpath=f"./data/{topic}/{year}/pdf", filename=f"{title}.pdf")

            # Parse the data of the paper from pdf
            reference = pdfParser.get_reference(fp=f"./data/{topic}/{year}/pdf/{title}.pdf")
            results["parsed_reference"] = reference

            # Get paper reference from Semantic Scholar
            sch_reference = sch_metadataExtractor.get_reference(arxiv_entry_id=entry_id)
            sch_reference_formatted = sch_metadataExtractor.format_ref(sch_reference)
            results["semanticScholarReference"]=sch_reference_formatted

            # Check if any references has published year greater than the original paper
            check1 = checker.check_greater_than_published_year(references=sch_reference,
                                                                 original_paper_year=year)
            results["check1"]={
                "description": "reference published year greater than the original paper or missing",
                "errors": check1
            }

            # # Check if there is any duplicates in the reference listed by Semantic Scholar
            check2 = checker.check_duplicate_entry(sch_reference)
            results["check2"]={
                "description": "similar reference with slightly different name in the reference list",
                "errors": check2
            }

            # # Check if there is any difference between the reference parsed from pdf and reference from SemScholar
            check3 = checker.check_reference_consistency(ref_sch=sch_reference, ref_metadata=reference)
            results["check3"]={
                "description": "The difference in the reference of the Semantic Scholar and parsed reference",
                "errors": check3
            }
            with open(f"./data/{topic}/{year}/sanity_check_results/{title}_{entry_id}.json", "w") as fp:
                json.dump(results, fp, indent=4)
            logging.info(f"End processing {title}")
        except:
            logging.info(f"Failed processing {title}")
            pass





