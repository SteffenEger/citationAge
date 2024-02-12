# Is there really a Citation Age Bias in NLP?

This repository contains code for our paper - [Is there really a Citation Age Bias in NLP](https://arxiv.org/abs/2401.03545). If you use it, please cite:

```
@misc{nguyen2024really,
      title={Is there really a Citation Age Bias in NLP?}, 
      author={Hoa Nguyen and Steffen Eger},
      year={2024},
      eprint={2401.03545},
      archivePrefix={arXiv},
      primaryClass={cs.DL}
}
```

# Project structure
crawler.py 
- This script is used to crawl the list of IDs of the publication  and fetch the references list from Semantic Scholar api.
compare.py
- This script download sample subset of papers PDF from arxiv, parses the pdf and performs the comparison automatically as defined in sanity_check.py
sanity_check.py 
- This scripts defines the classes of comparison we use to automatically compare the list of references we get from parsing the pdf with Science Parse and the reference provided on Semantic Scholar.
analyse.py
- miscelanneous processing.
Foler notebook:
- The folder contain jupyter notebook to generate the data statistics about the citation age.

The corresponding data can be found [here](https://drive.google.com/drive/folders/1k0GOvi9-m5Hrs4EO6O6iuskJOV7Oq5cl?usp=sharing).  

