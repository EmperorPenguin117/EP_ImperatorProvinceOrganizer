from collections import defaultdict
import pandas as pd
import numpy as np
def main():
    prov_list = [0, 1, 2]
    culture_list = ["aa", "", "a"]
    prov_names = ["a", "b", "c"]
    religion_list = ["r1", "r2", "r3"]
    for i in range(len(prov_list)):
        if len(culture_list[i]) == 0:
            print(f"{i+1} = {{\t#BLACK"
                  f"\n\t980.1.1 = {{"
                  f"\n\t\tculture = test_culture"
                  f"\n\t\treligion = test_faith"
                  f"\n\t\tholding = castle_holding"
                  f"\n\t}}"
                  f"\n}}\n")
        else:
            print(f"{i+1} = {{\t#{prov_names[i]}"
                  f"\n\t980.1.1 = {{"
                  f"\n\t\tculture = {culture_list[i]}"
                  f"\n\t\treligion = {religion_list[i]}"
                  f"\n\t\tholding = castle_holding"
                  f"\n\t}}"
                  f"\n}}\n")

if __name__ == '__main__':
    main()

