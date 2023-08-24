import os
import sys, numpy as np
import pandas as pd


def get_statistics(df, year):
    # Transform into age distance
    df = df.applymap(lambda x: year-x if x < year else 0)
    df['mean'] = df.mean(axis=1)
    df['median'] = df.median(axis=1)
    df['mode'] = df.mode(axis=1)

    print(df.head())
    mean = df['mean'].mean()

    return {"mean":mean}

def get_statistics_by_cat(cat_name):
    for year in range(2013, 2020):
        with open(f"data/{cat_name}/{year}/output.csv", "r") as fp:
            df = pd.read_csv(fp, header=0)
            # Get all col which refers to the ref-age
            col_names = [col_name for col_name in  df.columns if "ref age" in col_name]
            # Get dataframe of reference years
            ref_year_df = df[col_names]
            # Get all statistics
            statistics = get_statistics(ref_year_df, year)
            print(statistics)

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


if __name__ == "__main__":
    get_statistics_by_cat("cs.CV")
