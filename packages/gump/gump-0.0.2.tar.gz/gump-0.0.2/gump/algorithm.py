# Created on 21/05/2025
# Author: Frank Vega

import itertools
from . import utils

import networkx as nx
import aegypti.algorithm as algo

def find_clique(graph):
    """
    Compute the approximate clique set for an undirected graph by transforming it into a chordal graph.

    Args:
        graph (nx.Graph): A NetworkX Graph object representing the input graph.

    Returns:
        set: A set of vertex indices representing the approximate clique set.
             Returns an empty set if the graph is empty or has no edges.
    """
    def _is_complete_graph(G):
        """Returns True if G is a complete graph.
        
        Args:
            G (nx.Graph): A NetworkX Graph object to check.
        
        Returns:
            bool: True if G is a complete graph (every pair of nodes is connected), False otherwise.
        """
        n = G.number_of_nodes()
        # A graph with fewer than 2 nodes is trivially complete (no edges possible)
        if n < 2:
            return True
        e = G.number_of_edges()
        # A complete graph with n nodes has n*(n-1)/2 edges
        max_edges = (n * (n - 1)) / 2
        return e == max_edges
    
    # Validate that the input is an undirected NetworkX Graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
    
    # Handle the case of an empty graph (no nodes)
    if graph.number_of_nodes() == 0:
        return set()
    
    # Create a copy of the input graph to avoid modifying the original
    working_graph = graph.copy()
    
    # Remove self-loops, as they are irrelevant for clique detection
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
    
    # Identify and remove isolated nodes (degree 0), as they cannot be part of a clique
    isolates = list(nx.isolates(working_graph))
    working_graph.remove_nodes_from(isolates)
    
    # Initialize the approximate clique set; if there are isolates, pick one arbitrarily
    approximate_clique = {isolates.pop()} if isolates else set()
    
    # If the cleaned graph has no nodes left, return the initialized clique (possibly empty)
    if working_graph.number_of_nodes() == 0:
        return approximate_clique
    
    # Iterate over each connected component in the graph
    for component in nx.connected_components(working_graph):
        # Extract the subgraph for the current component
        subgraph = working_graph.subgraph(component)
        # Initialize a clique set for this component
        clique = set()
        while True:
            # Check if the subgraph is a complete graph (a clique)
            if _is_complete_graph(subgraph):
                # If it is, add all its nodes to the clique and stop processing this component
                clique.update(set(subgraph.nodes()))
                break    
            # Use the aegypti algorithm to find all triangles in the subgraph
            triangles = algo.find_triangle_coordinates(subgraph, first_triangle=False)
            # If no triangles are found, handle the remaining cases
            if triangles is None:
                # If there are edges, pick one edge's nodes as a minimal clique
                if subgraph.number_of_edges() > 0:
                    for u, v in subgraph.edges():
                        clique.update({u, v})
                        break    
                # If no edges but nodes remain, pick an arbitrary node
                elif subgraph.number_of_nodes() > 0:
                    arbitrary_node = next(iter(set(subgraph.nodes())))
                    clique.add(arbitrary_node)
                break    
            # Count how many triangles each node appears in
            count = {}
            for triangle in triangles:
                for u in triangle:
                    if u not in count:
                        count[u] = 1
                    else:
                        count[u] += 1
            # Select the triangle with the highest total node counts
            triangle = max(triangles, key=lambda x: sum(count[u] for u in x))
            # From that triangle, pick the node with the highest triangle count
            vertex = max(list(triangle), key=lambda x: count[x])
            # Add the selected vertex to the clique
            clique.add(vertex)
            # Reduce the subgraph to the neighbors of the selected vertex
            remaining = set(subgraph.neighbors(vertex))
            subgraph = subgraph.subgraph(remaining)
                
        # Keep the largest clique found across all components
        if len(clique) > len(approximate_clique):
            approximate_clique = clique

    # Return the largest approximate clique found
    return approximate_clique

def find_clique_brute_force(graph):
    """
    Computes an exact maximum clique in exponential time.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the exact clique, or None if the graph is empty.
    """

    
    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    n_vertices = len(graph.nodes())

    n_max_vertices = 0
    best_solution = None

    for k in range(1, n_vertices + 1): # Iterate through all possible sizes of the cover
        for candidate in itertools.combinations(graph.nodes(), k):
            clique_candidate = set(candidate)
            if utils.is_clique(graph, clique_candidate) and len(clique_candidate) > n_max_vertices:
                n_max_vertices = len(clique_candidate)
                best_solution = clique_candidate
                
    return best_solution


def find_clique_approximation(graph):
    """
    Computes an approximate clique in polynomial time with a polynomial-approximation ratio for undirected graphs.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the approximate clique, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    #networkx doesn't have a guaranteed maximum clique function, so we use approximation
    clique = nx.approximation.max_clique(graph)
    return clique