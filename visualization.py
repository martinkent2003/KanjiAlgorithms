import networkx as nx
import plotly.graph_objects as go
from parsing import parse_raw_data
from greedy import find_learning_path
import numpy as np

def create_kanji_graph(kanji_dict, path_nodes):
    """
    Create a directed graph containing only nodes in the paths
    """
    G = nx.DiGraph()
    
    # Add only nodes that are in the paths
    for kanji in path_nodes:
        if kanji in kanji_dict:
            obj = kanji_dict[kanji]
            G.add_node(
                kanji,
                strokes=obj.strokes,
                grade=obj.grade,
                jlpt=obj.jlpt,
                difficulty=obj.difficulty,
                kfreq=obj.kfreq
            )
    
    # Store all edges for each node (for click interaction)
    for kanji in path_nodes:
        if kanji in kanji_dict:
            obj = kanji_dict[kanji]
            for composed_kanji, weight in obj.composed:
                if composed_kanji in G:
                    G.add_edge(kanji, composed_kanji, weight=weight)
    
    return G

def get_path_edges(paths):
    """Extract all edges that are part of the learning paths"""
    path_edges = set()
    for path in paths:
        if path:
            for i in range(len(path) - 1):
                path_edges.add((path[i], path[i+1]))
    return path_edges

def create_interactive_plot(G, paths, path_info, kanji_dict):
    """
    Create interactive plotly visualization showing learning paths
    """
    print(f"Calculating layout for {G.number_of_nodes()} nodes...")
    
    # Use hierarchical layout for path visualization
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        pos = nx.kamada_kawai_layout(G)
    
    print("Creating traces...")
    
    path_edges = get_path_edges(paths)
    
    # Create edge traces - separate for path edges and other edges
    path_edge_x = []
    path_edge_y = []
    other_edge_x = []
    other_edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        if edge in path_edges:
            path_edge_x.extend([x0, x1, None])
            path_edge_y.extend([y0, y1, None])
        else:
            other_edge_x.extend([x0, x1, None])
            other_edge_y.extend([y0, y1, None])
    
    # Other edges (faded)
    other_edge_trace = go.Scatter(
        x=other_edge_x, y=other_edge_y,
        line=dict(width=0.3, color='#444'),
        hoverinfo='none',
        mode='lines',
        showlegend=False,
        name='other connections',
        opacity=0.3
    )
    
    # Path edges (highlighted)
    path_edge_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        line=dict(width=2, color='#00ff88'),
        hoverinfo='none',
        mode='lines',
        showlegend=False,
        name='learning path',
        opacity=0.8
    )
    
    # Identify which nodes are in paths
    path_nodes = set()
    source_nodes = set()
    target_nodes = set()
    
    for i, path in enumerate(paths):
        if path:
            path_nodes.update(path)
            source_nodes.add(path[0])
            target_nodes.add(path[-1])
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_hover = []
    node_color = []
    node_size = []
    node_symbol = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # Get node attributes
        attrs = G.nodes[node]
        difficulty = attrs['difficulty']
        strokes = attrs['strokes']
        grade = attrs['grade']
        jlpt = attrs['jlpt']
        kfreq = attrs['kfreq']
        degree = G.degree(node)
        
        # Determine node type
        if node in source_nodes:
            node_type = "SOURCE"
            color_val = 0.0  # Green
        elif node in target_nodes:
            node_type = "TARGET"
            color_val = 1.0  # Red
        else:
            node_type = "PATH"
            color_val = difficulty
        
        # Create hover text
        node_hover.append(
            f"<b>{node}</b> [{node_type}]<br>"
            f"Strokes: {strokes}<br>"
            f"Grade: {grade}<br>"
            f"JLPT: {jlpt}<br>"
            f"Freq: {kfreq}<br>"
            f"Difficulty: {difficulty:.3f}<br>"
            f"Connections: {degree}<br>"
            f"<i>Click to see all edges</i>"
        )
        
        node_color.append(color_val)
        
        # Size by type
        if node in source_nodes or node in target_nodes:
            node_size.append(20)
            node_symbol.append('diamond' if node in source_nodes else 'square')
        else:
            node_size.append(12)
            node_symbol.append('circle')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        textfont=dict(
            size=11, 
            color='white', 
            family='Arial, sans-serif'
        ),
        hoverinfo='text',
        hovertext=node_hover,
        marker=dict(
            showscale=True,
            colorscale='RdYlGn_r',
            size=node_size,
            color=node_color,
            symbol=node_symbol,
            colorbar=dict(
                thickness=15,
                title=dict(text='Difficulty', side='right'),
                xanchor='left',
                len=0.7
            ),
            line=dict(width=2, color='white'),
            opacity=0.95
        ),
        showlegend=False,
        name='kanji'
    )
    
    # Create figure
    fig = go.Figure(
        data=[other_edge_trace, path_edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text='<b>Kanji Learning Paths</b><br><sub>◆ = Source • ■ = Target • Green edges = Learning path</sub>',
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=100),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                fixedrange=False
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                fixedrange=False
            ),
            plot_bgcolor='#0f0f0f',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            width=1600,
            height=900,
            dragmode='pan',
            annotations=create_path_annotations(path_info)
        )
    )
    
    config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    }
    
    return fig, config

def create_path_annotations(path_info):
    """Create annotations showing path information"""
    annotations = []
    y_pos = 0.98
    
    for i, info in enumerate(path_info):
        annotations.append(dict(
            x=0.02,
            y=y_pos - (i * 0.06),
            xref='paper',
            yref='paper',
            text=f"Path {i+1}: {info['source']} → {info['target']} (weight: {info['weight']:.2f}, {info['steps']} steps)",
            showarrow=False,
            font=dict(size=11, color='#00ff88'),
            align='left',
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(0,0,0,0.6)',
            bordercolor='#00ff88',
            borderwidth=1,
            borderpad=4
        ))
    
    return annotations

def find_example_paths(kanji_dict):
    """Find 4-5 example learning paths"""
    
    # Example pairs: (source, target) - simple to complex
    examples = [
        ("一", "謝"),  # one to apologize
        ("人", "働"),  # person to work
        ("口", "話"),  # mouth to speak
        ("日", "曜"),  # sun/day to day of week
        ("木", "森"),  # tree to forest
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

def main():
    print("Loading kanji data...")
    kanji_dict = parse_raw_data()
    print(f"Loaded {len(kanji_dict)} kanji")
    
    # Find example learning paths
    paths, path_info, all_nodes = find_example_paths(kanji_dict)
    
    if not paths:
        print("No paths found!")
        return
    
    print(f"\nFound {len(paths)} paths with {len(all_nodes)} unique kanji")
    
    # Create graph with only path nodes
    print("\nCreating graph...")
    G = create_kanji_graph(kanji_dict, all_nodes)
    
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Print detailed path information
    print_path_details(paths, path_info, kanji_dict)
    
    # Create visualization
    print("\nGenerating visualization...")
    fig, config = create_interactive_plot(G, paths, path_info, kanji_dict)
    
    print("\nSaving to HTML...")
    fig.write_html(
        "kanji_learning_paths.html",
        config=config,
        include_plotlyjs='cdn'
    )
    print("✓ Visualization saved to kanji_learning_paths.html")
    
    print("\nOpening in browser...")
    fig.show(config=config)

if __name__ == '__main__':
    main()