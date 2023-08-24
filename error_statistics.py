import json
import os
import matplotlib.pyplot as plt
from pathlib import  Path

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

def plot_by_cat():
    """
    Plot by cat
    :return:
    """

if __name__ == '__main__':
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


