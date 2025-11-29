import networkx as nx
import itertools
import math

def create_pendant_path(n):
    G = nx.Graph()

    # Create the path
    for i in range(n):
        if i < n - 1:
            G.add_edge(f'V{i}', f'V{i+1}')

        # Attach a pendant to each vertex in the path
        G.add_edge(f'V{i}', f'P{i}')

    return G

def is_independent_set(G, vertex_set):
    # Check if the vertex set is independent of the graph
    for v1, v2 in itertools.combinations(vertex_set, 2):
        if G.has_edge(v1, v2):
            return False
    return True

def get_independent_sets_with_root(G, root, r):
    # Generate all independent sets of size r that include the given root
    independent_sets = []
    vertices = set(G.nodes())
    vertices.remove(root)

    for subset in itertools.combinations(vertices, r - 1):  # r-1 because root is included
        candidate_set = (root,) + subset
        if is_independent_set(G, candidate_set):
            independent_sets.append(candidate_set)

    return independent_sets

def count_independent_sets_for_pendants(n, r):
    # Count independent intersecting sets for each rooted pendant 1 to ceil(n/2)
    G = create_pendant_path(n)

    results = []
    limit = math.ceil(n / 2)

    for i in range(1, limit + 1):  # Start from 1 to limit
        root = f'P{i - 1}'  # Use P0 to Pceil(n/2)-1 in the graph
        independent_sets = get_independent_sets_with_root(G, root, r)
        results.append((f'P{i}', len(independent_sets)))  # Use P1 to Pceil(n/2) in the output

    # Sort roots by the number of independent families from greatest to least, then by root index least to greatest
    results.sort(key=lambda x: (-x[1], int(x[0][1:])))

    # Output the results
    for root, count in results:
        print(f"{root}: {count}")

# Example usage: path on 10 vertices choose 8
print(count_independent_sets_for_pendants(10,8))
