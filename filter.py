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
                    format='%(asctime)s : %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def check_high_or_low_citation_number():
    pass