import networkx as nx
try:
    import numpy as np
except ImportError:
    np = None  # If numpy is not available, set np to None

import random

def generator_connected_ug(n, p):
    if np is None:
        raise ImportError("This function requires numpy, which is not installed on your system.")

    # Generate a random tree with n nodes
    g = nx.random_tree(n)
    
    # Get the upper triangular indices for the adjacency matrix (excluding the diagonal)
    row_indices, col_indices = np.triu_indices(n, k=1)
    
    # For each pair of nodes, decide whether to add an edge based on probability p
    edges_to_add = np.random.rand(len(row_indices)) < p
    
    # Create a list of edges to add based on the random selection
    edges = [(row_indices[i], col_indices[i]) for i in range(len(edges_to_add)) if edges_to_add[i]]
    
    # Add the selected edges to the graph
    g.add_edges_from(edges)
    
    return g




# This function generates a connected Directed Acyclic Graph (DAG) with n nodes.
# It first creates a directed tree and then probabilistically adds edges with probability p.
# Each node has a maximum of `max_parents` parents, with the default value being 3.
# Additionally, the number of nodes with exactly 3 parents is constrained to not exceed 5% of the total number of nodes.

def generate_connected_dag(n, p, max_parents=3):
    """
    Generate a connected Directed Acyclic Graph (DAG)
    
    Parameters:
        n: Number of nodes
        p: Probability of adding an edge
        max_parents: Maximum number of parents allowed for each node (default is 3)
    
    Additional constraint:
        The number of nodes with 3 parents should not exceed 5% of the total number of nodes
    """
    # Calculate the maximum number of nodes that can have 3 parents (5% of n)
    max_4_parents = int(0.05 * n)
    current_4_parents = 0
    
    # Generate a directed tree
    tree = nx.DiGraph()
    tree.add_nodes_from([f"X{i}" for i in range(n)])
    
    # Build the connected tree structure
    for i in range(1, n):
        possible_parents = [
            f"X{j}" for j in range(i) 
            if tree.in_degree(f"X{j}") < max_parents and
            (tree.in_degree(f"X{j}") != max_parents - 1 or current_4_parents < max_4_parents)
        ]
        
        if possible_parents:
            parent = random.choice(possible_parents)
            tree.add_edge(parent, f"X{i}")
            if tree.in_degree(parent) == max_parents:
                current_4_parents += 1
    
    # Add additional edges based on probability p
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
                
            if random.random() < p:
                target_degree = tree.in_degree(f"X{j}")
                
                # Check all constraints
                if (target_degree < max_parents and 
                    (target_degree != max_parents - 1 or current_4_parents < max_4_parents)):
                    
                    new_tree = tree.copy()
                    new_tree.add_edge(f"X{i}", f"X{j}")
                    
                    if nx.is_directed_acyclic_graph(new_tree):
                        tree.add_edge(f"X{i}", f"X{j}")
                        if tree.in_degree(f"X{j}") == max_parents:
                            current_4_parents += 1
    
    # Final verification
    assert nx.is_directed_acyclic_graph(tree), "The generated graph is not a DAG"
    assert nx.is_weakly_connected(tree), "The graph is not connected"
    assert all(d <= max_parents for _, d in tree.in_degree()), f"There are nodes with more than {max_parents} parents"
    
    # Verify the 4-parent constraint
    nodes_with_4_parents = sum(1 for _, d in tree.in_degree() if d == max_parents)
    assert nodes_with_4_parents <= max_4_parents, f"The number of nodes with 4 parents exceeds {n*0.05}"
    
    return tree



