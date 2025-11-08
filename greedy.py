import heapq
import time
import random
import matplotlib.pyplot as plt
import math
import heapdict
from parsing import parse_raw_data

def measure_runtime(kanji_dict, trials=5):
    sizes = [100, 300, 600, 1000, 1500, len(kanji_dict)]
    results = []

    all_kanji = list(kanji_dict.keys())

    for n in sizes:
        if n > len(kanji_dict):
            break
        subset_keys = set(random.sample(all_kanji, n))
        subgraph = {k: v for k, v in kanji_dict.items() if k in subset_keys}
        
        source = random.choice(list(subgraph.keys()))

        total_time = 0.0
        for _ in range(trials):
            start = time.perf_counter()
            dijkstras(source, subgraph)
            end = time.perf_counter()
            total_time += (end - start)
        
        avg_time = total_time / trials
        results.append((n, avg_time))
        print(f"{n:5d} vertices → {avg_time:.6f} seconds (avg over {trials} runs)")

    print("\n=== Runtime Summary ===")
    for n, t in results:
        print(f"{n:5d} vertices | {t:.6f} s")
    
    return results

def plot_runtime(results):
    vertices = [r[0] for r in results]
    runtimes = [r[1] for r in results]

    plt.figure(figsize=(8, 5))
    plt.plot(vertices, runtimes, 'o-', label="Measured Runtime", linewidth=2)

    # should be O(V log V) for reference (scaled for visual comparison)
    scale = runtimes[0] / (vertices[0] * math.log(vertices[0]))
    theoretical = [scale * v * math.log(v) for v in vertices]
    plt.plot(vertices, theoretical, '--', label="O(V log V) (scaled)", color='gray')

    plt.title("Dijkstra Runtime Complexity (Empirical vs Theoretical)")
    plt.xlabel("Number of Vertices (V)")
    plt.ylabel("Average Runtime (seconds)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

def dijkstras(source_kanji: str, kanji_dict: dict):
    if source_kanji not in kanji_dict:
        print(f"Error : {source_kanji} not found in kanji dictionary")
        return None, None
    
    #create a set of infinite distances for each node(except source=0)
    distances = {}
    #create a null set of predecessors for each node 
    predecessors = {}
    #create empty priority queue pq
    pq = heapdict.heapdict()
    for kanji in kanji_dict:
        if kanji == source_kanji:
            distances[kanji] = 0
            pq[kanji]=0
        else: 
            distances[kanji] = float('inf')
            pq[kanji] = float('inf')
        predecessors[kanji] = None
        #for each vertice in vertices, insert (v, dist(v)) (infinity for now)
        
    

    # while pq is not empty
    while pq:
        #get the vertex (u) with the shortest distance to source(first iteration is the source)
        current_dist, u = pq.popitem()
        #since we might come accros repeated vertices in the pq, check the updated distance 

        
        kanji_obj = kanji_dict.get(u)
        if not kanji_obj:
            continue
        #for each edge (u,v) starting from u 
        for v, edge_weight in kanji_obj.composed:
            if v not in kanji_dict:
                continue
            new_dist = distances[u] + edge_weight
            if new_dist<distances[v]:
                #insert new dist(v) in the priority queue (no updating/replacing in python)
                distances[v] = new_dist
                pq[v] = new_dist
                predecessors[v] = u
                
    return distances, predecessors

def reconstruct_path(target_kanji: str, predecessors: dict):
    if target_kanji not in predecessors: return None
    path = []
    current = target_kanji
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    path.reverse()
    return path

def find_learning_path(source_kanji: str, target_kanji: str, kanji_dict: dict):
    distances, predecessors = dijkstras(source_kanji, kanji_dict)
    
    if distances is None:
        return None, None
    
    if target_kanji not in distances:
        print(f"Error: {target_kanji} not found in dictionary")
        return None, None
    
    if distances[target_kanji] == float('inf'):
        print(f"No path exists from {source_kanji} to {target_kanji}")
        return None, None
    
    path = reconstruct_path(target_kanji, predecessors)
    total_difficulty = distances[target_kanji]
    
    return path, total_difficulty
def find_example_paths(kanji_dict):
    examples = [
        ("一", "謝"),  
        ("人", "働"),  
        ("口", "話"),  
        ("森", "鑑"),  
        ("醸", "森"),  
    ]
    
    paths = []
    path_info = []
    all_nodes = set()
    
    print("\n=== Finding Learning Paths ===")
    for source, target in examples:
        if source in kanji_dict and target in kanji_dict:
            print(f"\nPath {len(paths)+1}: {source} → {target}")
            path, difficulty = find_learning_path(source, target, kanji_dict)
            
            if path:
                paths.append(path)
                all_nodes.update(path)
                path_info.append({
                    'source': source,
                    'target': target,
                    'weight': difficulty,
                    'steps': len(path)
                })
                print(f"  Found path with {len(path)} steps, weight: {difficulty:.2f}")
                print(f"  Path: {' → '.join(path)}")
            else:
                print(f"  No path found")
    
    return paths, path_info, all_nodes


if __name__ == "__main__":
    kanji_metrics_dict = parse_raw_data()
    print(f"Loaded {len(kanji_metrics_dict)} kanji\n")
    #
    paths, path_info, all_nodes = find_example_paths(kanji_metrics_dict)
    
    if not paths:
        print("No paths found!")
    else:
        print(f"\nFound {len(paths)} paths with {len(all_nodes)} unique kanji")
    
    results = measure_runtime(kanji_metrics_dict)
    plot_runtime(results)
    # Example 1: Find path from simple kanji to complex kanji
    #source = "験" 
    #target = "賢"  
    
    #print(f"Finding learning path from {source} to {target}...")
    #path, difficulty = find_learning_path(source, target, kanji_metrics_dict)
    
    #if path:
    #    print(f"\nOptimal learning path (total weight: {difficulty:.3f}):")
    #    for i, kanji in enumerate(path):
    #        kanji_obj = kanji_metrics_dict[kanji]
    #        print(f"  {i+1}. {kanji} (strokes: {kanji_obj.strokes}, "
    #              f"grade: {kanji_obj.grade}, JLPT: {kanji_obj.jlpt})")
    