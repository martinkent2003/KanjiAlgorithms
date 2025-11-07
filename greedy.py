import heapq

from parsing import parse_raw_data

def dijkstras(source_kanji: str, kanji_dict: dict):
    if source_kanji not in kanji_dict:
        print(f"Error : {source_kanji} not found in kanji dictionary")
        return None, None
    
    #create a set of infinite distances for each node(except source=0)
    distances = {}
    #create a null set of predecessors for each node 
    predecessors = {}
    #create empty priority queue pq
    pq = []
    for kanji in kanji_dict:
        if kanji == source_kanji:
            distances[kanji] = 0
        else: 
            distances[kanji] = float('inf')
        predecessors[kanji] = None
        #for each vertice in vertices, insert (v, dist(v)) (infinity for now)
        heapq.heappush(pq, (distances[kanji], kanji))
    

    # while pq is not empty
    while pq:
        #get the vertex (u) with the shortest distance to source(first iteration is the source)
        current_dist, u = heapq.heappop(pq)
        #since we might come accros repeated vertices in the pq, check the updated distance 
        if current_dist > distances[u]:
            continue 
        kanji_obj = kanji_dict.get(u)
        #for each edge (u,v) starting from u 
        for v, edge_weight in kanji_obj.composed:
            if v not in kanji_dict:
                continue
            new_dist = distances[u] + edge_weight
            if new_dist<distances[v]:
                #insert new dist(v) in the priority queue (no updating/replacing in python)
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))
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
    """Find 4-5 example learning paths"""
    
    # Example pairs: (source, target) - simple to complex
    examples = [
        ("一", "謝"),  # one to apologize
        ("人", "働"),  # person to work
        ("口", "話"),  # mouth to speak
        ("森", "鑑"),  # sun/day to day of week
        ("醸", "森"),  # tree to forest
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

def print_path_details(paths, path_info, kanji_dict):
    """Print detailed information about each path"""
    print("\n" + "="*60)
    print("LEARNING PATH DETAILS")
    print("="*60)
    
    for i, (path, info) in enumerate(zip(paths, path_info)):
        print(f"\n--- Path {i+1}: {info['source']} → {info['target']} ---")
        print(f"Total Weight: {info['weight']:.3f}")
        print(f"Steps: {info['steps']}\n")
        
        for j, kanji in enumerate(path):
            obj = kanji_dict[kanji]
            print(f"  {j+1}. {kanji:2s} | Strokes: {obj.strokes:2d} | "
                  f"Grade: {obj.grade} | JLPT: {obj.jlpt} | "
                  f"Difficulty: {obj.difficulty:.3f}")
        print()

if __name__ == "__main__":
    kanji_metrics_dict = parse_raw_data()
    print(f"Loaded {len(kanji_metrics_dict)} kanji\n")
    #
    paths, path_info, all_nodes = find_example_paths(kanji_metrics_dict)
    
    if not paths:
        print("No paths found!")
    else:
        print(f"\nFound {len(paths)} paths with {len(all_nodes)} unique kanji")
    
    
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
    