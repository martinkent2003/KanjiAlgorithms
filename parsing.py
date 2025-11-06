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
    composed: list #used to create the directed weighted graph 

def calculate_difficulty(strokes, grade, jlpt, kfreq):
    """
    Calculate benefit score as a ratio of difficulty to usability
    Weights on differnt aspects
    """
    stroke_score = strokes/29.0
    grade_score = grade/7.0
    jlpt_score = (6-jlpt)/5.0
    freq_score = 1.0 / (kfreq +1) if kfreq > 0 else 1.0

    difficulty = (
        0.2 * stroke_score +
        0.2 * grade_score +
        0.3 * jlpt_score + 
        0.2 * freq_score
    )

    return difficulty

def parse_raw_data():
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
    #first iteration creates all kanji objects 
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

    #second pass populates composed lists with (kanji,difficulty) tuple
    for kanji, kanji_obj in kanji_metrics_dict.items():
        if kanji in reverse_dict:
            composed_with_difficulty = []
            for composed_kanji in reverse_dict[kanji]:
                if composed_kanji in kanji_metrics_dict:
                    target = kanji_metrics_dict[composed_kanji]
                    difficulty = calculate_difficulty(
                        target.strokes,
                        target.grade,
                        target.jlpt,
                        target.kfreq
                    )
                    composed_with_difficulty.append((composed_kanji, difficulty))
            #presorting to make djikstras easier later on
            composed_with_difficulty.sort(key=lambda x: x[1])
            kanji_obj.composed = composed_with_difficulty

    return kanji_metrics_dict


if __name__ == '__main__':
    #first get the radicals and kanji from krad, reorder for correct direction in graph
    kanji_metrics_dict = parse_raw_data() 

    print(f"total kanjidict: {len(kanji_metrics_dict)}")
    print(len(kanji_metrics_dict.items()))
    for radical, kanjiclass in list(kanji_metrics_dict.items())[10:11]:
        print(f"{radical}: strokes:{kanjiclass.strokes}, grade:{kanjiclass.grade}, jlpt:{kanjiclass.jlpt}, composed:{kanjiclass.composed}")


