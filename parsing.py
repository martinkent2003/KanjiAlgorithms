import pandas as pd
import json
import itertools
from dataclasses import dataclass

@dataclass
class kanji_class:
    id: str
    kanji: str
    strokes: int
    grade: int
    jlpt: int
    rfreq: int
    kfreq: int
    composed: list

if __name__ == '__main__':
    #first get the radicals and kanji from krad, reorder for correct direction in graph
    json_path = "krad.json"
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    kanji_dict = {entry["literal"]: entry["components"] for entry in data}
    reverse_dict = {}
    for k, v in list(kanji_dict.items()):
        for i in v:
            #print(f"{i}:{k}")
            if i!=k:
                reverse_dict.setdefault(i,[]).append(k)

    
    for radical, kanji_list in list(reverse_dict.items())[48:50]:
        print(f"{radical}: {kanji_list}")

    kanji_metrics_dict = {}

    df = pd.read_csv("kanjimetrics.csv")
    for _, row in df.iterrows():
        kanji = row['Kanji']
        composed_kanji = reverse_dict.get(kanji, [])
        kanji_obj = kanji_class(
            id = str(row['id']),
            kanji = kanji,
            strokes =int(row['Strokes']),
            grade = int(row['Grade']),
            jlpt = int(row['JLPT-test']),
            rfreq=int(row['Radical Freq.']),
            kfreq=int(row['Kanji Frequency without Proper Nouns']),
            composed = composed_kanji
        )
        kanji_metrics_dict[kanji] = kanji_obj

    print(f"total kanjidict: {len(kanji_metrics_dict)}")

    for radical, kanjiclass in list(kanji_metrics_dict.items())[10:20]:
        print(f"{radical}: strokes:{kanjiclass.strokes}, grade:{kanjiclass.grade}, jlpt:{kanjiclass.jlpt}, composed:{kanjiclass.composed}")
    print(len(reverse_dict))

