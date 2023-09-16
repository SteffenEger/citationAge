import json


if __name__ == "__main__":
    for year in range(2013, 2017):
        with open(f"data/cs.AI/{year}/cs.AI_cs.LG_output.json", "r") as fp:
            content = json.load(fp)
            cs_AI = []
            cs_LG = []
            for item in content:
            #     if "cs.LG" in item["cat"]:
            #         cs_LG.append(item)
                if "cs.AI" in item["cat"]:
                    cs_AI.append(item)
            with open(f"data/cs.AI/{year}/output.json", "w") as fp:
                json.dump(cs_AI, fp, indent=4)
            # with open(f"data/cs.LG/{year}/output.json", "w") as fp:
            #     json.dump(cs_LG, fp, indent=4)