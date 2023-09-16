import json
import os
import math
import sys, numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

def get_statistics(df, year):
    # Transform into age distance
    df = df.applymap(lambda x: year-x if x < year else 0)
    df['mean'] = df.mean(axis=1)
    df['median'] = df.median(axis=1)
    df['mode'] = df.mode(axis=1)

    print(df.head())
    mean = df['mean'].mean()

    return {"mean":mean}

def get_statistics_by_cat(main_year, cat_name):
    with open(f"data/{cat_name}/{main_year}/output.csv", "r") as fp:
        df = pd.read_csv(fp, header=0)
        # Get all col which refers to the ref-age
        col_names = [col_name for col_name in  df.columns if "ref age" in col_name]
        # Get dataframe of reference years
        ref_year = df[col_names].to_numpy()

        results = []
        for item in ref_year.tolist():
            citationAges = []
            clean_citation = []
            for year in item:
                if np.isnan(year) != True:
                    if int(year) < (main_year-20):
                        clean_citation.append((main_year-20))
                    else:
                        clean_citation.append(int(year))
            for year in clean_citation:
                citationAges.append(main_year-year)

            if clean_citation:
                results.append(sum(citationAges)/len(citationAges))
        return sum(results)/len(results)

def plot(fp):
    # ag = []
    agFirst = []
    agSecond = []
    rec = []
    csv_reader = csv.reader(open(fp), delimiter=",")

    # for iline,line in enumerate(sys.stdin):
    iline = 0
    papers, papersFirst = 0, 0
    years = set()
    N = int(sys.argv[2])
    # ,year,title,link,Citation Count,Fields of Study,ref
    for line in csv_reader:
        if iline == 0:
            iline += 1
            continue
        # x = line.strip().split(",")
        # x = line.split(",,")
        x = line
        ##print(x)
        year = int(x[1])
        years.add(year)
        title = x[2]
        link = x[3]
        month = int(link.split("/")[-1].split(".")[0][-2:])
        if month < 7:
            ag = agFirst
            # papersFirst = papers
            # papers = 0
        else:
            ag = agSecond
        # print("---",x[4])
        try:
            cc = int(float(x[4]))
        except ValueError:
            sys.stderr.write("CITATION ERROR?" + " ".join(x) + "\n")
        if cc < N: continue
        refs = x[6:]
        # print("###",refs,"+++",x[6])
        try:
            int(float(x[6]))
        except ValueError:
            sys.stderr.write("ERROR? " + " ".join(x) + "\n")
            # sys.exit(1)

        ages = {}
        activ_ref = 0
        for ref in refs:
            try:
                r = int(float(ref))
            except ValueError:
                break
            age = year - r
            if age > 20: age = 21
            ages[age] = ages.get(age, 0) + 1
            activ_ref += 1
            # if age<0: print("###",x)
        # print(ages)
        mean = []
        recent = ages.get(0, 0)  # +ages.get(0,1)
        if len(ages) > 5 < len(ages) < 10:
            # print(title,month,link,ages)
            pass

        # print(recent,activ_ref)
        for age in ages:
            mean.append(age)
        if mean != []:
            m = np.mean(mean)
            ag.append(m)
            recent_share = recent / activ_ref
            rec.append(recent_share)
            # print(refs)
            if month < 7:
                papersFirst += 1
            else:
                papers += 1

    print(years, "1", "%.3f +- %.2f" % (np.mean(agFirst), np.std(agFirst)), "\t%.3f" % np.mean(rec), "\t", papersFirst)
    print(years, "2", "%.3f +- %.2f" % (np.mean(agSecond), np.std(agSecond)), "\t%.3f" % np.mean(rec), "\t", papers)

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

                # # First half
                # first_half_citationAges = [int(ref["year"]) - year for ref in item["reference"]]
                # first_half_avgAges = sum(first_half_citationAges)/(len(first_half_citationAges))
                # first_half.append(first_half_avgAges)
                #
                # # Second half
                # second_half_citationAges = [int(ref["year"]) - year for ref in item["reference"]]
                # second_half_avgAges = sum(second_half_citationAges)/(len(second_half_citationAges))
                # second_half.append(second_half_avgAges)

    #     results.append({
    #         "joint": sum(joint_avgAges)/len(joint_avgAges),
    #                    #"first_half": sum(first_half)/len(first_half),
    #                    # "second_half": sum(second_half)/len(second_half)
    #          })
    # return results

def plot_new(results):
    """

    :param results:
    :return:
    """
    pass

if __name__ == "__main__":
    age_2020_2023 = []
    for year in range(2020, 2024):
        stats = get_summary_by_year(year, cat="cs.CV")
        age_2020_2023.append(stats)


    age_2013_2019 = []
    for year in range(2013, 2020):
        age_2013_2019.append(get_statistics_by_cat(cat_name="cs.CV", main_year=year))

    stat = age_2013_2019 + age_2020_2023
    print(stat)
    plt.bar([year for year in range(2013,2024)], stat)
    plt.legend()

    plt.ylabel('Average citation counts')
    plt.xlabel('Year')
    plt.title(" Average citation count for cs.CV")

    plt.show()