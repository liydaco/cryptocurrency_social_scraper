import csv
import os

script_dir = os.path.dirname(__file__)
rel_path = "./commonwordlist.csv"
abs_file_path = os.path.join(script_dir, rel_path)

file = open(abs_file_path)

wordscsv = csv.DictReader(file)

def get_common_words():
    commonwords = []
    for col in wordscsv:
     commonwords.append(col['commonwordlist'].upper())
    return commonwords

