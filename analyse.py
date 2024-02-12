import json
import os
import statistics
import math
from pathlib import  Path
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def get_statistics_by_cat(cat, threshold):
    data = []
    for year in range(2013, 2024):
        if year != 2017:
            with open(f"data/{cat}/{year}/output_{year}_new.csv", "r") as fp:
                df = pd.read_csv(fp, header=0)
                # Get all col which refers to the ref-age
                col_names = [col_name for col_name in  df.columns if "ref age" in col_name]
                # Get dataframe of reference years
                ref_year = df[col_names].to_numpy().tolist()
                pub_years = []
                for i in range(len(ref_year)):
                    pub_years.extend(ref_year[i])

                pub_ages = normalize_age(pub_years, year, threshold)
                mean = statistics.mean(pub_ages)
                mode = statistics.mode(pub_ages)
                median = statistics.median(pub_ages)
                data.append([year, mean, mode, median])

    # form dataframe from data
    df = pd.DataFrame(data, columns=["Year", "Mean", "Mode", "Median"])

    # plot multiple columns such as population and year from dataframe
    df.plot(x="Year", y=[ "Mean", "Mode", "Median"], kind="bar", figsize=(10, 10), fontsize=20)
    # Save plot
    plt.savefig(f'data/{cat}/{cat}_threshold_{threshold}.png', format='png', dpi=300)

    return df
def get_summary_by_year(main_year, cat):
    """
    Get the average citation counts for a category by year
    :param :
    :return:
    """
    with open(f"data/{cat}/{main_year}/output.json", "r") as fp:
        items = json.load(fp)
        #first_half = []
        #second_half = []
        joint = []

        for item in items:
            # Joint
            citation_years = [ref["year"] for ref in item["reference"] if ref["year"] is not None]
            clean_citation_years = []
            for year in citation_years:
                if year < (main_year-20):
                    clean_citation_years.append(main_year-20)
                else:
                    clean_citation_years.append(year)
            joint_citationAges = [main_year - year for year in clean_citation_years]

            if joint_citationAges:
                joint_avgAges = sum(joint_citationAges)/(len(joint_citationAges))
        return joint_avgAges
def analyse_science_parse_results(cat):
    """
    statistics_pdfparse_500.json
    :return:
    """
    # Loading data
    data = []
    for year in range(2013, 2024):
        if os.path.exists(f"data/{cat}/{year}/statistics_pdfparse_500.json"):
            with open(f"data/{cat}/{year}/statistics_pdfparse_500.json", "r") as fp:
                content = json.load(fp)
                item = [year]+list(content.values())
                data.append(item)

    # form dataframe from data
    df = pd.DataFrame(data, columns=["Year", "Mean", "Mode", "Median"])

    # plot multiple columns such as population and year from dataframe
    df.plot(x="Year", y=[ "Mean", "Mode", "Median"], kind="bar", figsize=(10, 10), fontsize=20)

    # Save plot
    plt.savefig(f'data/{cat}/{cat}_scienceparse.png', format='png', dpi=300)
def normalize_age(ref_years, year, threshold=20):
    ages = []

    for pub_year in ref_years:
        if pub_year and math.isnan(float(pub_year)) is not True:
            if year - int(pub_year) > threshold:
                pub_year = year-threshold
            ages.append(year-int(pub_year))
    return ages
def analyse_semsch_results(cat, threshold=20):
    # Loading data
    results = []
    for year in range(2013, 2024):
        if os.path.exists(f"data/{cat}/{year}/output.json"):
            with open(f"data/{cat}/{year}/output.json", "r") as fp:
                content = json.load(fp)
                reference_year = []
                #reference_year_first = []
                #reference_year_second = []
                for paper in content:
                    reference_year.extend([ref["year"] for ref in paper["reference"]])

                reference_age = normalize_age(reference_year, year, threshold)
                #reference_year_first = normalize_age(reference_year_first, year)
                #reference_year_second = normalize_age(reference_year_second, year)
                year_mean= statistics.mean(reference_age)
                year_mode = statistics.mode(reference_age)
                year_median = statistics.median(reference_age)

                item = [year, year_mean, year_mode, year_median]
                results.append(item)

    # Form dataframe from data
    df = pd.DataFrame(results, columns=["Year", "Mean", "Mode", "Median"])

    # Plot multiple columns such as population and year from dataframe
    df.plot(x="Year", y=["Mean", "Mode", "Median"], kind="bar", figsize=(20, 20))

    # Save plot
    plt.savefig(f'data/{cat}/{cat}_threshold_{threshold}.png', format='png', dpi=300)

    return df
def analyse(cat, threshold=20):
    results = []
    for year in range(2013, 2024):
        if os.path.exists(f"data/{cat}/{year}/output.json"):
            with open(f"data/{cat}/{year}/output.json", "r") as fp:
                content = json.load(fp)
                reference_year = []
                #reference_year_first = []
                #reference_year_second = []
                for paper in content:
                    reference_year.extend([ref["year"] for ref in paper["reference"]])

                reference_age = normalize_age(reference_year, year, threshold)
                #reference_year_first = normalize_age(reference_year_first, year)
                #reference_year_second = normalize_age(reference_year_second, year)
                year_mean= statistics.mean(reference_age)
                year_mode = statistics.mode(reference_age)
                year_median = statistics.median(reference_age)

                item = [year, year_mean, year_mode, year_median]
                results.append(item)

        elif os.path.exists(f"data/{cat}/{year}/output_{year}_new.csv"):
            with open(f"data/{cat}/{year}/output_{year}_new.csv", "r") as fp:
                df = pd.read_csv(fp, header=0)
                # Get all col which refers to the ref-age
                col_names = [col_name for col_name in  df.columns if "ref age" in col_name]
                # Get dataframe of reference years
                ref_year = df[col_names].to_numpy().tolist()
                pub_years = []
                for i in range(len(ref_year)):
                    pub_years.extend(ref_year[i])

                pub_ages = normalize_age(pub_years, year, threshold)
                mean = statistics.mean(pub_ages)
                mode = statistics.mode(pub_ages)
                median = statistics.median(pub_ages)
                results.append([year, mean, median])
        else:
            pass

    # form dataframe from data
    df = pd.DataFrame(results, columns=["Year", "Mean", "Mode", "Median"])

    # plot multiple columns such as population and year from dataframe
    df.plot(x="Year", y=["Mean","Mode", "Median"], kind="bar", figsize=(10, 10), fontsize=20)
    # Save plot
    plt.savefig(f'data/{cat}/{cat}_threshold_{threshold}.png', format='png', dpi=300)

    return df

def analyse_highly_cited(cat, threshold=20):
    results = []
    for year in range(2013, 2024):
        if os.path.exists(f"data/{cat}/{year}/output.json"):
            with open(f"data/{cat}/{year}/output.json", "r") as fp:
                content = json.load(fp)
                reference_year = []
                #reference_year_first = []
                #reference_year_second = []
                for paper in content:
                    for ref in paper["reference"]:
                        if ref["influentialCitationCount"]:
                            if ref["influentialCitationCount"] >= 20:
                                reference_year.append(ref["year"])

                reference_age = normalize_age(reference_year, year, threshold)
                #reference_year_first = normalize_age(reference_year_first, year)
                #reference_year_second = normalize_age(reference_year_second, year)
                year_mean= statistics.mean(reference_age)
                year_mode = statistics.mode(reference_age)
                year_median = statistics.median(reference_age)

                item = [year, year_mean, year_mode, year_median]
                results.append(item)

    # form dataframe from data
    df = pd.DataFrame(results, columns=["Year", "Mean", "Mode", "Median"])

    return df

def concat_science_parse_result(cat):
    results = []
    for year in range(2013, 2024):
        with open(f"data/{cat}/{year}/statistics_pdfparse_500.json", "r") as fp:
            content = json.load(fp)
            results.append(content)

    df = pd.DataFrame(results)
    df.to_csv(f"data/{cat}/statistics_sp_500.csv", index=False)

def plot(docs, basepath):
    """
    Plot by cat and year
    :param docs:
    :param basepath:
    :return:
    """
    error1 = []
    error2 = []
    error3 = []

    for doc in docs:
        with open(os.path.join(basepath, doc), "r") as fp:
            content = json.load(fp)

        # Count error 1
        error1.append(len(content["check1"]["errors"]))

        # Count error 2
        error2.append(len(content["check2"]["errors"]))

        # Count error 3
        error3.append(len(content["check3"]["errors"]))

    # Plot error 1
    save_path = Path(basepath).parents[0]
    fig1 = plt.figure(figsize=(10, 15))
    plt.title('Reference published year greater than the original paper or missing', fontsize=20)
    plt.xlabel('# numbers of errors')
    plt.ylabel('# number of docs')
    plt.hist(error1)
    fig1.savefig(os.path.join(save_path, 'error1.png'))
    plt.close()


    # Plot error 2
    fig2 = plt.figure(figsize=(10, 15))
    plt.title('Reference published year greater than the original paper or missing')
    plt.xlabel('# number of docs')
    plt.ylabel('# numbers of errors')
    plt.hist(error2)
    fig2.savefig(os.path.join(save_path, 'error2.png'))
    plt.title('Similar reference with slightly different name in the reference list')
    plt.close()

    # Plot error 3
    fig3 = plt.figure(figsize=(10, 15))
    plt.xlabel('# number of docs')
    plt.ylabel('# numbers of errors')
    plt.hist(error3)
    fig3.savefig(os.path.join(save_path, 'error3.png'))
    plt.title('The difference in the reference of the Semantic Scholar and parsed reference')
    plt.close()

if __name__ == "__main__":
    cats =  [
            #"cs.DL",
            #"cs.DM",
            "cs.SI",
            #"econ.EM",
            #"math.GM"
              ]
    years = [i for i in range(2013,2024)]

    for year in years:
        for cat in cats:
            basepath = f"data/{cat}/{year}/sanity_check_results/"
            files = os.listdir(basepath)
            plot(files, basepath)

    cats = [
            #"cs.AI",
            #"cs.CV",
            #"cs.CL",
            #"cs.DL",
            #"cs.DM",
            #"cs.LG",
            #"cs.SI",
            #"econ.EM",
            #"hep-th",
            "math.GM"
    ]

    for cat in cats:
       df =  analyse_highly_cited(cat)
       df.to_csv(f"data/{cat}/statistics_influencial.csv")