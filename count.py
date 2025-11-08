import time
import math
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import pandas as pd



def merge_and_count(left: List[int], right: List[int]) -> Tuple[List[int], int]:
    merged = []
    i = j = inv_count = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); inv_count += len(left) - i; j += 1
    merged.extend(left[i:]); merged.extend(right[j:])
    return merged, inv_count

def count_inversions(arr: List[int]) -> Tuple[List[int], int]:
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, invL = count_inversions(arr[:mid])
    right, invR = count_inversions(arr[mid:])
    merged, invC = merge_and_count(left, right)
    return merged, invL + invR + invC


def load_external_order(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    order = [line.split(",")[0][0] for line in lines]  # first Kanji only
    return order

def load_kanji_difficulty(metrics_path: str) -> Dict[str, float]:
    df = pd.read_csv(metrics_path, dtype={"Kanji": str})
    df.rename(
        columns={
            "Kanji": "kanji",
            "Strokes": "strokes",
            "Grade": "grade",
            "JLPT-test": "jlpt",
            "Kanji Frequency without Proper Nouns": "kfreq",
        },
        inplace=True,
    )

    df["difficulty"] = df.apply(
        lambda r: (
            0.2 * (r["strokes"] / 29.0) +
            0.2 * (r["grade"] / 7.0) +
            0.3 * ((6 - r["jlpt"]) / 5.0) +
            0.2 * (1.0 / (r["kfreq"] + 1) if r["kfreq"] > 0 else 1.0)
        ),
        axis=1
    )

    return {r["kanji"]: r["difficulty"] for _, r in df.iterrows()}


def experiment_runtime(metrics_path: str, order_path: str):
    difficulty_map = load_kanji_difficulty(metrics_path)
    ext_order = load_external_order(order_path)

    shared = [k for k in ext_order if k in difficulty_map]
    sorted_kanji = sorted(shared, key=lambda k: difficulty_map[k])
    rank_map = {k: i for i, k in enumerate(sorted_kanji)}

    n_values = list(range(100, min(2100, len(shared)) + 1, 100))
    times = []

    for n in n_values:
        subset = shared[:n]
        arr = [rank_map[k] for k in subset if k in rank_map]

        start = time.perf_counter_ns()
        count_inversions(arr)
        end = time.perf_counter_ns()

        elapsed_ms = (end - start) / 1e6
        times.append(elapsed_ms)

    return n_values, times



def plot_runtime(n_values, times):
    plt.figure(figsize=(8, 5))
    plt.scatter(n_values, times, label="Measured runtime", color="blue")

    # scale O(n log n) curve
    c = times[-1] / (n_values[-1] * math.log2(n_values[-1]))
    theoretical = [c * n * math.log2(n) for n in n_values]
    plt.plot(n_values, theoretical, color="red", linestyle="--", label="O(n log n) reference")

    plt.title("Merge Sort Inversion Counting Runtime")
    plt.xlabel("n (Kanji subset size)")
    plt.ylabel("Time (ms)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()



def compare_orders(metrics_path: str, order_files: Dict[str, str]):
    difficulty_map = load_kanji_difficulty(metrics_path)
    sorted_kanji = sorted(difficulty_map.keys(), key=lambda k: difficulty_map[k])
    rank_map = {k: i for i, k in enumerate(sorted_kanji)}

    for name, path in order_files.items():
        ext_order = load_external_order(path)
        shared = [k for k in ext_order if k in rank_map]
        arr = [rank_map[k] for k in shared]

        _, inversions = count_inversions(arr)
        total_pairs = len(arr) * (len(arr) - 1) / 2
        inversion_rate = inversions / total_pairs if total_pairs > 0 else 0

        print(f"=== {name} Order ===")
        print(f"Shared Kanji count: {len(shared)}")
        print(f"Total inversions: {inversions}")
        print(f"Inversion rate: {inversion_rate:.4f} ({inversion_rate*100:.2f}%)\n")




if __name__ == "__main__":
    metrics_path = "KanjiMetrics.csv"

    external_orders = {
        "RTK": "RTKKanjiOrder.csv",
        "Genki": "GenkiKanjiOrder.csv",
        "Kodansha": "KodanshaKanjiOrder.csv",
    }

    # Runtime experiment: Commented out because figure only needs to be generated once
    # n_vals, times = experiment_runtime(metrics_path, external_orders["RTK"])
    # plot_runtime(n_vals, times)

    # Print inversion results for all external orders
    compare_orders(metrics_path, external_orders)
