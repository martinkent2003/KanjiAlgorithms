import heapq

from parsing import parse_raw_data

def djkistras(source_kanji: str, kanji_dict: dict):
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
        if u in visited:
            continue
        #for each edge (u,v) starting from u 
            #if the dist(v) > dist(u)+ edge weight(uv)
                #update the new dist(v) in the priority queue
                #update the new dist(v) in the set of distances
                #update the predecessor to v as u
    return

if  __name__ == "__main__":
    #first get the radicals and kanji from krad, reorder for correct direction in graph
    kanji_metrics_dict = parse_raw_data() 